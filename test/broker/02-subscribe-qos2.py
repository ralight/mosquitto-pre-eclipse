#!/usr/bin/python

# Test whether a SUBSCRIBE to a topic with QoS 2 results in the correct SUBACK packet.

import socket
from struct import *

connect_packet = pack('BBBB6sBBBBBB19s', 16, 12+2+19,0,6,"MQIsdp",3,2,0,60,0,19,"subscribe-qos2-test")
connack_packet = pack('BBBB', 32, 2, 0, 0);

subscribe_packet = pack('BBBBBB9sB', 130, 2+2+9+1, 0, 1, 0, 9, "qos2/test", 2)
suback_packet = pack('BBBBB', 144, 2+1, 0, 1, 2)

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(("localhost", 1888))
sock.send(connect_packet)
connack_recvd = sock.recv(256)

if connack_recvd != connack_packet:
	print "FAIL: Connect failed."
	exit(1)

sock.send(subscribe_packet)
suback_recvd = sock.recv(256)
sock.close()

if suback_recvd != suback_packet:
	(cmd, rl, midh, midl, qos) = unpack('BBBBB', suback_recvd)
	print "FAIL: Expected 144,3,0,1,2 got " + str(cmd) + "," + str(rl) + "," + str(midh) + "," + str(midl) + "," + str(qos)
	exit(1)
