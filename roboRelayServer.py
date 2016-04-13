#!/usr/bin/env python
import socket
import threading
import signal

clientPort = 5454
carPort = 4545

s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(('', clientPort))
s.listen(10)

carSock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
carSock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
carSock.bind(('', carPort))
carSock.listen(10)

threads = []
inputQueue = []
carIsConnected = False
validInput = ['w','a','s','d']

# Semaphores to control access to shared resources inputQueue and carIsConnected
inputSem = threading.Semaphore()
carConnectionSem = threading.Semaphore()


# Receive data from client and put it in the input queue
# todo: send comformation message(is car connected)?
def communicateWithClient(c, addr):
	r = c.recv(32)
	carConnectionSem.acquire()
	if (carIsConnected and r in validInput):
		inputSem.acquire()
		inputQueue.append(r)
		inputSem.release()
	c.close()
	carConnectionSem.release()
	return

# Send data from the input queue to the car
def communicateWithCar():

	while(1):
		# Wait for car to connect
		c, addr = carSock.accept()
		isConnected = True
		global carIsConnected
		carConnectionSem.acquire()
		carIsConnected = True
		carConnectionSem.release()
		
		print('Car connected')

		# While car is connected, if input queue is not empty send input to car
		while(isConnected):
			if(len(inputQueue) > 0):
				inputSem.acquire()
				try:
					c.send(inputQueue[0])
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

# def signal_handler(signal, frame):
# 	for t in threads:
# 		print 'k'
# 		t.exit()
# 	print('Shutting down server')
# 	sys.exit(0)


# Start car communication thread
# signal.signal(signal.SIGINT, signal_handler)
t = threading.Thread(target=communicateWithCar)
threads.append(t)
t.start()

# Wait for a clients to connect
while 1:
	conn, addr = s.accept()
	print('Connection received')
	t = threading.Thread(target=communicateWithClient, args=(conn, addr))
	threads.append(t)
	t.start()
