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

# Semaphore to cotrol access to shared resource inputQueue
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
# todo needs to handle disconnects
def communicateWithCar():

	while(1):
		#wait for car to connect
		c, addr = carSock.accept()

		# While car is connected, if input queue is not empty send input to car
		while(1):
			if(len(inputQueue) > 0):
				try:
					sem.acquire()
					c.send(inputQueue[0])
					inputQueue.pop(0)
					sem.release()
				except socket.error, e:
					print 'Socket error: '+ e + '\nClosing connection'
					c.close()
					return
		c.close()
		return




signal.signal(signal.SIGINT, signal_handler)
t = threading.Thread(target=communicateWithCar)
threads.append(t)
t.start()
# wait for a clients to connect
while 1:
	conn, addr = s.accept()
	print('Connection received')
	t = threading.Thread(target=communicateWithClient, args=(conn, addr))
	threads.append(t)
	t.start()
