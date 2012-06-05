#!/usr/bin/python

# Test whether a UNSUBSCRIBE to a topic with QoS 0 results in the correct UNSUBACK packet.
# This doesn't assume a subscription exists.

import subprocess
import socket
import time
from struct import *

rc = 1
mid = 53
keepalive = 60
connect_packet = pack('!BBH6sBBHH21s', 16, 12+2+21,6,"MQIsdp",3,2,keepalive,21,"unsubscribe-qos0-test")
connack_packet = pack('!BBBB', 32, 2, 0, 0);

unsubscribe_packet = pack('!BBHH9s', 162, 2+2+9, mid, 9, "qos0/test")
unsuback_packet = pack('!BBH', 176, 2, mid)

broker = subprocess.Popen(['../../src/mosquitto', '-p', '1888'], stderr=subprocess.PIPE)

try:
	time.sleep(0.5)

	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.connect(("localhost", 1888))
	sock.send(connect_packet)
	connack_recvd = sock.recv(256)

	if connack_recvd != connack_packet:
		print("FAIL: Connect failed.")
	else:
		sock.send(unsubscribe_packet)
		unsuback_recvd = sock.recv(256)

		if unsuback_recvd != unsuback_packet:
			(cmd, rl, mid_recvd) = unpack('!BBH', unsuback_recvd)
			print("FAIL: Expected 176,2,"+str(mid)+" got " + str(cmd) + "," + str(rl) + "," + str(mid_recvd))
		else:
			rc = 0

	sock.close()
finally:
	broker.terminate()
	broker.wait()

exit(rc)

