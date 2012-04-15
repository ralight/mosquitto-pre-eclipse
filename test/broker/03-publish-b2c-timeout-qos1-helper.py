#!/usr/bin/python

# Test whether a PUBLISH to a topic with QoS 2 results in the correct packet flow.

import subprocess
import socket
import time
from struct import *

rc = 1
keepalive = 60
connect_packet = pack('!BBH6sBBHH11s', 16, 12+2+11,6,"MQIsdp",3,2,keepalive,11,"test-helper")
connack_packet = pack('!BBBB', 32, 2, 0, 0);

mid = 128
publish_packet = pack('!BBH17sH15s', 48+2, 2+17+2+15, 17, "qos1/timeout/test", mid, "timeout-message")
puback_packet = pack('!BBH', 64, 2, mid)

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(("localhost", 1888))
sock.send(connect_packet)
connack_recvd = sock.recv(256)

if connack_recvd != connack_packet:
	print "FAIL in helper: Connect failed."
else:
	sock.send(publish_packet)
	puback_recvd = sock.recv(256)

	if puback_recvd != puback_packet:
		(cmd, rl, mid_recvd) = unpack('!BBH', puback_recvd)
		print "FAIL in helper: Expected 64,2," + str(mid) + " got " + str(cmd) + "," + str(rl) + "," + str(mid_recvd)
	else:
		rc = 0

sock.close()
	
exit(rc)

