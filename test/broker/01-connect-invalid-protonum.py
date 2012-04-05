#!/usr/bin/python

# Test whether a CONNECT with an invalid protocol number results in the correct CONNACK packet.

import socket
from struct import *

keepalive = 10
connect_packet = pack('!BBH6sBBHH20s', 16, 12+2+20,6,"MQIsdp",0,2,keepalive,20,"connect-invalid-test")
connack_packet = pack('!BBBB', 32, 2, 0, 1);

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(("localhost", 1888))
sock.send(connect_packet)
connack_recvd = sock.recv(256)
sock.close()

if connack_recvd != connack_packet:
	(cmd, rl, resv, rc) = unpack('!BBBB', connack_recvd)
	print "FAIL: Expected 32,2,0,1 got " + str(cmd) + "," + str(rl) + "," + str(resv) + "," + str(rc)
	exit(1)

