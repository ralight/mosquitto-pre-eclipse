#!/usr/bin/python

# Test whether a valid CONNECT results in the correct CONNACK packet.

import socket
from struct import *

connect_packet = pack('!BBH6sBBBBH20s', 16, 12+2+20,6,"MQIsdp",3,2,0,10,20,"connect-success-test")
connack_packet = pack('!BBBB', 32, 2, 0, 0);

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(("localhost", 1888))
sock.send(connect_packet)
connack_recvd = sock.recv(256)
sock.close()

if connack_recvd != connack_packet:
	(cmd, rl, resv, rc) = unpack('!BBBB', connack_recvd)
	print "FAIL: Expected 32,2,0,0 got " + str(cmd) + "," + str(rl) + "," + str(resv) + "," + str(rc)
	exit(1)

