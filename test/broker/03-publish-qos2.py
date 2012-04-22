#!/usr/bin/python

# Test whether a PUBLISH to a topic with QoS 2 results in the correct packet flow.

import subprocess
import socket
import time
from struct import *

rc = 1
keepalive = 60
connect_packet = pack('!BBH6sBBHH13s', 16, 12+2+13,6,"MQIsdp",3,2,keepalive,13,"pub-qos2-test")
connack_packet = pack('!BBBB', 32, 2, 0, 0);

mid = 312
publish_packet = pack('!BBH13sH7s', 48+4, 2+13+2+7, 13, "pub/qos2/test", mid, "message")
pubrec_packet = pack('!BBH', 80, 2, mid)
pubrel_packet = pack('!BBH', 96, 2, mid)
pubcomp_packet = pack('!BBH', 112, 2, mid)

broker = subprocess.Popen(['../../src/mosquitto', '-p', '1888'], stderr=subprocess.PIPE)

try:
	time.sleep(0.1)

	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.connect(("localhost", 1888))
	sock.send(connect_packet)
	connack_recvd = sock.recv(256)

	if connack_recvd != connack_packet:
		print("FAIL: Connect failed.")
	else:
		sock.send(publish_packet)
		pubrec_recvd = sock.recv(256)

		if pubrec_recvd != pubrec_packet:
			(cmd, rl, mid_recvd) = unpack('!BBH', pubrec_recvd)
			print("FAIL: Expected 80,2," + str(mid) + " got " + str(cmd) + "," + str(rl) + "," + str(mid_recvd))
		else:
			sock.send(pubrel_packet)
			pubcomp_recvd = sock.recv(256)

			if pubcomp_recvd != pubcomp_packet:
				(cmd, rl, mid_recvd) = unpack('!BBH', pubcomp_recvd)
				print("FAIL: Expected 112,2," + str(mid) + " got " + str(cmd) + "," + str(rl) + "," + str(mid_recvd))
			else:
				rc = 0

	sock.close()
finally:
	broker.terminate()

exit(rc)

