#!/usr/bin/python

# Test whether a CONNECT with a too-long client id results in the correct CONNACK packet.

import subprocess
import socket
import time
from struct import *

rc = 0
keepalive = 10
connect_packet = pack('!BBH6sBBHH30s', 16, 12+2+30,6,"MQIsdp",3,2,keepalive,30,"connect-invalid-id-test-------")
connack_packet = pack('!BBBB', 32, 2, 0, 2);

broker = subprocess.Popen(['../../src/mosquitto', '-p', '1888'], stderr=subprocess.PIPE)

try:
	time.sleep(0.1)

	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.connect(("localhost", 1888))
	sock.send(connect_packet)
	connack_recvd = sock.recv(256)
	sock.close()

	if connack_recvd != connack_packet:
		(cmd, rl, resv, rc) = unpack('!BBBB', connack_recvd)
		print "FAIL: Expected 32,2,0,3 got " + str(cmd) + "," + str(rl) + "," + str(resv) + "," + str(rc)
		rc = 1
finally:
	broker.terminate()

exit(rc)

