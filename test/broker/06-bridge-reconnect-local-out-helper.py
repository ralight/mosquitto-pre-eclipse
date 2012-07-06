#!/usr/bin/python

import subprocess
import socket
import time
from struct import *

rc = 1
keepalive = 60
connect_packet = pack('!BBH6sBBHH11s', 16, 12+2+11,6,"MQIsdp",3,2,keepalive,11,"test-helper")
connack_packet = pack('!BBBB', 32, 2, 0, 0);

publish_packet = pack('!BBH16s24s', 48, 2+16+24, 16, "bridge/reconnect", "bridge-reconnect-message")

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(("localhost", 1889))
sock.send(connect_packet)
connack_recvd = sock.recv(256)

if connack_recvd != connack_packet:
	print("FAIL in helper: Connect failed.")
else:
	sock.send(publish_packet)
	rc = 0

sock.close()
	
exit(rc)

