#!/usr/bin/python

# Test whether a PUBLISH to a topic with QoS 1 results in the correct PUBACK packet.

import socket
from struct import *

connect_packet = pack('BBBB6sBBBBBB13s', 16, 12+2+13,0,6,"MQIsdp",3,2,0,60,0,13,"pub-qos1-test")
connack_packet = pack('BBBB', 32, 2, 0, 0);

publish_packet = pack('BBBB13sBB7s', 48+2, 2+13+2+7, 0, 13, "pub/qos1/test", 0, 17, "message")
puback_packet = pack('BBBB', 64, 2, 0, 17)

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
	(cmd, rl, midh, midl) = unpack('BBBB', puback_recvd)
	print "FAIL: Expected 64,2,0,17 got " + str(cmd) + "," + str(rl) + "," + str(midh) + "," + str(midl)
	exit(1)
