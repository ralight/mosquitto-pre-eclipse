#!/usr/bin/python

# Test whether a PUBLISH to a topic with QoS 2 results in the correct packet
# flow. This test introduces delays into the flow in order to force the broker
# to send duplicate PUBREC and PUBCOMP messages.

import subprocess
import socket
import time
from struct import *

rc = 0
keepalive = 600
connect_packet = pack('!BBH6sBBHH21s', 16, 12+2+21,6,"MQIsdp",3,2,keepalive,21,"pub-qos2-timeout-test")
connack_packet = pack('!BBBB', 32, 2, 0, 0);

mid = 1926
publish_packet = pack('!BBH13sH15s', 48+4, 2+13+2+15, 13, "pub/qos2/test", mid, "timeout-message")
pubrec_packet = pack('!BBH', 80, 2, mid)
pubrec_dup_packet = pack('!BBH', 80+8, 2, mid)
pubrel_packet = pack('!BBH', 96, 2, mid)
pubcomp_packet = pack('!BBH', 112, 2, mid)

broker = subprocess.Popen(['../../src/mosquitto', '-c', '03-publish-timeout-qos2.conf'])

try:
	time.sleep(0.1)

	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.settimeout(8) # 8 seconds timeout is longer than 5 seconds message retry.
	sock.connect(("localhost", 1888))
	sock.send(connect_packet)
	connack_recvd = sock.recv(256)

	if connack_recvd != connack_packet:
		print "FAIL: Connect failed."
		rc = 1
	else:
		sock.send(publish_packet)
		pubrec_recvd = sock.recv(256)

		if pubrec_recvd != pubrec_packet:
			(cmd, rl, mid_recvd) = unpack('!BBH', pubrec_recvd)
			print "FAIL: Expected 80,2," + str(mid) + " got " + str(cmd) + "," + str(rl) + "," + str(mid_recvd)
			rc = 1
		else:
			pubrec_recvd = sock.recv(256)

			if pubrec_recvd != pubrec_dup_packet:
				(cmd, rl, mid_recvd) = unpack('!BBH', pubrec_recvd)
				print "FAIL: Expected 88,2," + str(mid) + " got " + str(cmd) + "," + str(rl) + "," + str(mid_recvd)
				rc = 1
			else:
				sock.send(pubrel_packet)
				pubcomp_recvd = sock.recv(256)

				if pubcomp_recvd != pubcomp_packet:
					(cmd, rl, mid_recvd) = unpack('!BBH', pubcomp_recvd)
					print "FAIL: Expected 112,2," + str(mid) + " got " + str(cmd) + "," + str(rl) + "," + str(mid_recvd)
					rc = 1

	sock.close()
finally:
	broker.terminate()

exit(rc)

