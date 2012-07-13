#!/usr/bin/python

# Test whether a connection is denied if it provides a correct username but
# incorrect password.

import subprocess
import socket
import time
from struct import *

rc = 1
keepalive = 10
connect_packet = pack('!BBH6sBBHH22sH4sH8s', 16, 12+2+22+2+4+2+8,6,"MQIsdp",3,194,keepalive,22,"connect-uname-pwd-test",4,"user",8,"password")
connack_packet = pack('!BBBB', 32, 2, 0, 0);

broker = subprocess.Popen(['../../src/mosquitto', '-c', '01-connect-uname-password-success.conf'], stderr=subprocess.PIPE)

try:
	time.sleep(0.5)

	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.connect(("localhost", 1888))
	sock.send(connect_packet)
	connack_recvd = sock.recv(256)
	sock.close()

	if connack_recvd != connack_packet:
		(cmd, rl, resv, ret) = unpack('!BBBB', connack_recvd)
		print("FAIL: Expected 32,2,0,0 got " + str(cmd) + "," + str(rl) + "," + str(resv) + "," + str(ret))
	else:
		rc = 0
finally:
	broker.terminate()
	broker.wait()

exit(rc)

