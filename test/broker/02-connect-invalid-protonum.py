#!/usr/bin/python

import socket
from struct import *

connect_packet = pack('bbbb6sbbbbbb20s', 16, 12+2+20,0,6,"MQIsdp",0,2,0,10,0,20,"connect-invalid-test")
connack_packet = pack('bbbb', 32, 2, 0, 1);

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(("localhost", 1888))
sock.send(connect_packet)
connack_recvd = sock.recv(256)
sock.close()

if connack_recvd != connack_packet:
	exit(1)

