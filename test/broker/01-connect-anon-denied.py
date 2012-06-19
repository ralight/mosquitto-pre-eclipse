#!/usr/bin/python

# Test whether an anonymous connection is correctly denied.

import subprocess
import socket
import time
from struct import *

rc = 1
keepalive = 10
connect_packet = pack('!BBH6sBBHH17s', 16, 12+2+17,6,"MQIsdp",3,2,keepalive,17,"connect-anon-test")
connack_packet = pack('!BBBB', 32, 2, 0, 5);

broker = subprocess.Popen(['../../src/mosquitto', '-c', '01-connect-anon-denied.conf'], stderr=subprocess.PIPE)

try:
	time.sleep(0.5)

	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.connect(("localhost", 1888))
	sock.send(connect_packet)
	connack_recvd = sock.recv(256)
	sock.close()

	if connack_recvd != connack_packet:
		(cmd, rl, resv, rc) = unpack('!BBBB', connack_recvd)
		print("FAIL: Expected 32,2,0,5 got " + str(cmd) + "," + str(rl) + "," + str(resv) + "," + str(rc))
	else:
		rc = 0
finally:
	broker.terminate()
	broker.wait()

exit(rc)

