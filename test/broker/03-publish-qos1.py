#!/usr/bin/python

# Test whether a PUBLISH to a topic with QoS 1 results in the correct PUBACK packet.

import socket
from struct import *

mid = 19
connect_packet = pack('!BBH6sBBBBH13s', 16, 12+2+13,6,"MQIsdp",3,2,0,60,13,"pub-qos1-test")
connack_packet = pack('!BBBB', 32, 2, 0, 0);

publish_packet = pack('!BBH13sH7s', 48+2, 2+13+2+7, 13, "pub/qos1/test", mid, "message")
puback_packet = pack('!BBH', 64, 2, mid)

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(("localhost", 1888))
sock.send(connect_packet)
connack_recvd = sock.recv(256)

if connack_recvd != connack_packet:
	print "FAIL: Connect failed."
	exit(1)

sock.send(publish_packet)
puback_recvd = sock.recv(256)
sock.close()

if puback_recvd != puback_packet:
	(cmd, rl, mid_recvd) = unpack('!BBH', puback_recvd)
	print "FAIL: Expected 64,2,"+str(mid)+" got " + str(cmd) + "," + str(rl) + "," + str(mid_recvd)
	exit(1)
