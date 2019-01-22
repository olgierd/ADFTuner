#!/usr/bin/python

import serial, socket, time


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('localhost', 7356))

ser = serial.Serial('/dev/ttyUSB0', 9600)


lastf = 0

while True:
	s.send('f\n')
	ans = int(s.recv(20))
	if ans != lastf:
		print ans, lastf
		ser.write(str(ans/10)+'X')
		lastf = ans
	time.sleep(0.2)

