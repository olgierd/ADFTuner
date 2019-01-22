#!/usr/bin/python
# -*- coding: utf-8 -*-

# de SQ3SWF

import serial, socket, time, sys
import matplotlib.pyplot as plt
import numpy as np

if len(sys.argv) < 4:
	print "Usage: " + sys.argv[0] + " Fstart(MHz) Fstop(MHz) Step(kHz) calfile.csv(optional)"
	sys.exit(1)

fstart = int(float(sys.argv[1])*1000000)
fstop = int(float(sys.argv[2])*1000000)
step = int(float(sys.argv[3])*1000) # kHz

# for calibration, run without last argument and pipe the output to > file.csv
# argv > 4 == calibration file provided
if len(sys.argv) > 4:
	f = open(sys.argv[4]).read().splitlines()
	dictio = {}
	for x in f:
		q = x.split(' ')
		dictio[int(q[0])] = float(q[1])
	print "Read calibration data."
	exit

# gqrx socket - enable in gqrx!
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('localhost', 7356))

# DDS
ser = serial.Serial('/dev/ttyUSB0', 9600)

time.sleep(2)
lastf = 0

lab = [x/1000000.0 for x in range(fstart,fstop,step)]
rls = []

ser.write(str(int(fstart/10))+'X')
s.send('F ' + str(fstart) + '\n')
q=s.recv(30)
time.sleep(0.3)

for x in range(fstart,fstop,step):
	time.sleep(0.02)
	ser.write(str(int(x/10))+'X') # tune DDS
	s.send('F ' + str(x) + '\n')	# tune GQRX
	q = s.recv(30)	# read tuning reply from GQRX
        sig = []
        for i in range(5):
	    time.sleep(0.1)
	    s.send('l\n')	# ask for signal level
            a = float(s.recv(30)[:-1])	# read signal level
            if a<0.0:
                sig.append(a)
        rl=max(sig)
	if len(sys.argv) < 5: # no calibration - raw value
		print x/10,  "{:.2f}".format(rl)
		rls.append(rl)
	else:	# including calibration - subtract the received value and calibration data
		rl -= dictio[x/10]
		try:
			swr = (1+10**(rl/20))/(1-10**(rl/20))
		except:
			swr = 100
		print x/10, str(rl).replace('.', ','), "{0:.2f}".format(swr)
		rls.append(rl)


ser.write(str(int(14430000))+'X')

plt.title(str(fstart/1000) + " to " + str(fstop/1000) + " kHz.")
plt.ylim([min(rls),0]) 		# autoscale to min db
plt.plot(lab, [-10]*len(lab))	# add -10 and -20 dB lines
plt.plot(lab, [-20]*len(lab))	#
plt.plot(lab, rls)
plt.show()

