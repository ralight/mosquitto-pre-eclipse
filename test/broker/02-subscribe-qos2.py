#!/usr/bin/python

# Test whether a SUBSCRIBE to a topic with QoS 2 results in the correct SUBACK packet.

import subprocess
import socket
import time
from struct import *

rc = 0
mid = 3
keepalive = 60
connect_packet = pack('!BBH6sBBHH19s', 16, 12+2+19,6,"MQIsdp",3,2,keepalive,19,"subscribe-qos2-test")
connack_packet = pack('!BBBB', 32, 2, 0, 0);

subscribe_packet = pack('!BBHH9sB', 130, 2+2+9+1, mid, 9, "qos2/test", 2)
suback_packet = pack('!BBHB', 144, 2+1, mid, 2)

broker = subprocess.Popen(['../../src/mosquitto', '-p', '1888'])

try:
	time.sleep(0.1)

	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.connect(("localhost", 1888))
	sock.send(connect_packet)
	connack_recvd = sock.recv(256)

	if connack_recvd != connack_packet:
		print "FAIL: Connect failed."
		rc = 1
	else:
		sock.send(subscribe_packet)
		suback_recvd = sock.recv(256)

		if suback_recvd != suback_packet:
			(cmd, rl, mid_recvd, qos) = unpack('!BBHB', suback_recvd)
			print "FAIL: Expected 144,3,"+str(mid)+",2 got " + str(cmd) + "," + str(rl) + "," + str(mid_recvd) + "," + str(qos)
			rc = 1

	sock.close()
finally:
	broker.terminate()

exit(rc)

