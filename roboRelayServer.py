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

# Semaphore to control access to shared resource inputQueue
sem = threading.Semaphore()


# Receive data from client and put it in the input queue
def communicateWithClient(c, addr):
	r = c.recv(32)
	sem.acquire()
	inputQueue.append(r)
	sem.release()
	c.close()
	return

# Send data from the input queue to the car
def communicateWithCar():

	while(1):
		# Wait for car to connect
		c, addr = carSock.accept()
		isConnected = True
		print('Car connected')

		# While car is connected, if input queue is not empty send input to car
		while(isConnected):
			if(len(inputQueue) > 0):
				sem.acquire()
				try:
					c.send(inputQueue[0])
					inputQueue.pop(0)
				except socket.error, e:
					print 'Socket error: Car disconnected'
					isConnected = False
				sem.release()
					
		c.close()

# def signal_handler(signal, frame):
# 	for t in threads:
# 		print 'k'
# 		t.exit()
# 	print('Shutting down server')
# 	sys.exit(0)


# Start car communication thread
signal.signal(signal.SIGINT, signal_handler)
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
