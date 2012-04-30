#!/usr/bin/python

# Test whether a client will is transmitted correctly.

import subprocess
import socket
import time
from struct import *

rc = 1
mid = 53
keepalive = 60
connect_packet = pack('!BBH6sBBHH14s', 16, 12+2+14,6,"MQIsdp",3,2,keepalive,14,"will-qos0-test")
connack_packet = pack('!BBBB', 32, 2, 0, 0);

subscribe_packet = pack('!BBHH14sB', 130, 2+2+14+1, mid, 14, "will/qos0/test", 0)
suback_packet = pack('!BBHB', 144, 2+1, mid, 0)

publish_packet = pack('!BBH14s12s', 48, 2+14+12, 14, "will/qos0/test", "will-message")

broker = subprocess.Popen(['../../src/mosquitto', '-p', '1888'], stderr=subprocess.PIPE)

try:
	time.sleep(0.5)

	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.settimeout(30)
	sock.connect(("localhost", 1888))
	sock.send(connect_packet)
	connack_recvd = sock.recv(256)

	if connack_recvd != connack_packet:
		print("FAIL: Connect failed.")
	else:
		sock.send(subscribe_packet)
		suback_recvd = sock.recv(256)

		if suback_recvd != suback_packet:
			(cmd, rl, mid_recvd, qos) = unpack('!BBHB', suback_recvd)
			print("FAIL: Expected 144,3,"+str(mid)+",0 got " + str(cmd) + "," + str(rl) + "," + str(mid_recvd) + "," + str(qos))
		else:
			will = subprocess.Popen(['./07-will-qos0-helper.py'])
			will.wait()

			publish_recvd = sock.recv(256)

			if publish_recvd != publish_packet:
				print("FAIL: Received publish not correct.")
				print("Received: "+publish_recvd+" length="+str(len(publish_recvd)))
				print("Expected: "+publish_packet+" length="+str(len(publish_packet)))
			else:
				rc = 0

	sock.close()
finally:
	broker.terminate()
	broker.wait()

exit(rc)

