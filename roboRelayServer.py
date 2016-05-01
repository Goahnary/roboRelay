#!/usr/bin/env python

# roboRelayServer
# https://github.com/Goahnary/roboRelay
# Socket server to act as middleman and pass commands from the client to the car
# Requires: websocket_server.py

import socket
import threading
import signal
import sys
from websocket_server import WebsocketServer

clientPort = 8008
carPort = 1337

carSock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
carSock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
carSock.bind(('', carPort))
carSock.listen(10)

threads = []
inputQueue = []
carIsConnected = False
clientIsConnected = False
runServer = True
validInput = ["MOVE FORWARD", "MOVE LEFT", "MOVE RIGHT", "MOVE BACKWARD", "ACTION STOP"]

# Semaphores to control access to shared resources inputQueue and carIsConnected
inputSem = threading.Semaphore()
carConnectionSem = threading.Semaphore()


def onClientConnection(client, server):
	global clientIsConnected
	clientIsConnected = True
	print('Client connected')

def onClientDisconnection(client, server):
	global clientIsConnected
	clientIsConnected = False
	# Send car diconnect message
	carConnectionSem.acquire()
	if (carIsConnected):
		inputSem.acquire()
		inputQueue.append('ACTION DISCONNECT')
		inputSem.release()
	carConnectionSem.release()
	print('Client disconnected')

# Receive data from client and put it in the input queue
def communicateWithClient(client, server, msg):
	print('recv: ' + msg)
	carConnectionSem.acquire()
	if (carIsConnected and msg in validInput):
		inputSem.acquire()
		inputQueue.append(msg)
		inputSem.release()
	carConnectionSem.release()

# Websocket to talk to client
websocket = WebsocketServer(clientPort)
websocket.set_fn_new_client(onClientConnection)
websocket.set_fn_client_left(onClientDisconnection)
websocket.set_fn_message_received(communicateWithClient)

# Handle car communications
def communicateWithCar():

	while(runServer):
		# Wait for car to connect
		c, addr = carSock.accept()
		isConnected = True
		global carIsConnected
		carConnectionSem.acquire()
		carIsConnected = True
		carConnectionSem.release()
		
		print('Car connected')

		# Receive CONNECT CAR from car
		r = c.recv(128)
		# Notify car of the clients connection status
		# Once client has also connected begin communication
		if(not clientIsConnected):
			c.send("CONTROL DISCONNECTED\r\n")

			while(not clientIsConnected and runServer):
				r = c.recv(128)
				if(r == "CONTROL STATUS\r\n"):
					try:
						c.send("CONTROL DISCONNECTED\r\n")
					except socket.error, e:
						print 'Socket error: Car disconnected'
						isConnected = False
						carConnectionSem.acquire()
						carIsConnected = False
						carConnectionSem.release()

		c.send("CONTROL CONNECTED\r\n")

		# While car is connected: if input queue is not empty, send input to car
		while(isConnected and runServer):
			if(len(inputQueue) > 0):
				inputSem.acquire()
				try:
					c.send(inputQueue[0]+"\r\n")
					inputQueue.pop(0)
				except socket.error, e:
					print 'Socket error: Car disconnected'
					isConnected = False
					carConnectionSem.acquire()
					carIsConnected = False
					carConnectionSem.release()
					# Clear input queue
					del inputQueue[:]
				inputSem.release()
					
		c.close()

def signal_handler(signal, frame):
	print('\nShutting down server..')

	global carIsConnected
	global runServer
	carConnectionSem.acquire()
	runServer = False

	# If car is not connected: connect to self as car then close connection
	# so thread will continue and check if it needs to stop
	if(not carIsConnected):
		s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
		s.connect(('127.0.0.1',carPort))
		s.close()

	carConnectionSem.release()

	sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)


# Start car communication thread
t = threading.Thread(target=communicateWithCar)
threads.append(t)
t.start()
print 'Listening on port', carPort, 'for car'

# Start websocket to communicate with client
websocket.run_forever()
