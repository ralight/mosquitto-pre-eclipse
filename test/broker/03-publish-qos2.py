#!/usr/bin/python

# Test whether a PUBLISH to a topic with QoS 2 results in the correct packet flow.

import socket
from struct import *

connect_packet = pack('BBBB6sBBBBBB13s', 16, 12+2+13,0,6,"MQIsdp",3,2,0,60,0,13,"pub-qos2-test")
connack_packet = pack('BBBB', 32, 2, 0, 0);

publish_packet = pack('BBBB13sBB7s', 48+4, 2+13+2+7, 0, 13, "pub/qos2/test", 1, 12, "message")
pubrec_packet = pack('BBBB', 80, 2, 1, 12)
pubrel_packet = pack('BBBB', 96, 2, 1, 12)
pubcomp_packet = pack('BBBB', 112, 2, 1, 12)

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(("localhost", 1888))
sock.send(connect_packet)
connack_recvd = sock.recv(256)

if connack_recvd != connack_packet:
	print "FAIL: Connect failed."
	exit(1)

sock.send(publish_packet)
pubrec_recvd = sock.recv(256)

if pubrec_recvd != pubrec_packet:
	(cmd, rl, midh, midl) = unpack('BBBB', pubrec_recvd)
	print "FAIL: Expected 80,2,1,12 got " + str(cmd) + "," + str(rl) + "," + str(midh) + "," + str(midl)
	exit(1)

sock.send(pubrel_packet)
pubcomp_recvd = sock.recv(256)
sock.close()

if pubcomp_recvd != pubcomp_packet:
	(cmd, rl, midh, midl) = unpack('BBBB', pubcomp_recvd)
	print "FAIL: Expected 112,2,1,12 got " + str(cmd) + "," + str(rl) + "," + str(midh) + "," + str(midl)
	exit(1)

