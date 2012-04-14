#!/usr/bin/python

# Test whether a SUBSCRIBE to a topic with QoS 2 results in the correct SUBACK packet.

import subprocess
import socket
import time
from struct import *
from os import environ

rc = 0
mid = 3265
keepalive = 60
connect_packet = pack('!BBH6sBBHH21s', 16, 12+2+21,6,"MQIsdp",3,2,keepalive,21,"pub-qos2-timeout-test")
connack_packet = pack('!BBBB', 32, 2, 0, 0);

subscribe_packet = pack('!BBHH17sB', 130, 2+2+17+1, mid, 17, "qos2/timeout/test", 2)
suback_packet = pack('!BBHB', 144, 2+1, mid, 2)

mid = 1
publish_packet = pack('!BBH17sH15s', 48+4, 2+17+2+15, 17, "qos2/timeout/test", mid, "timeout-message")
publish_dup_packet = pack('!BBH17sH15s', 48+8+4, 2+17+2+15, 17, "qos2/timeout/test", mid, "timeout-message")
pubrec_packet = pack('!BBH', 80, 2, mid)
pubrel_packet = pack('!BBH', 96+2, 2, mid)
pubrel_dup_packet = pack('!BBH', 96+8+2, 2, mid)
pubcomp_packet = pack('!BBH', 112, 2, mid)

broker = subprocess.Popen(['../../src/mosquitto', '-c', '03-publish-b2c-timeout-qos2.conf'], stderr=subprocess.PIPE)

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
		sock.send(subscribe_packet)
		suback_recvd = sock.recv(256)

		if suback_recvd != suback_packet:
			(cmd, rl, mid_recvd, qos) = unpack('!BBHB', suback_recvd)
			print "FAIL: Expected 144,3,"+str(mid)+",2 got " + str(cmd) + "," + str(rl) + "," + str(mid_recvd) + "," + str(qos)
			rc = 1
		else:
			pub = subprocess.Popen(['./03-publish-b2c-timeout-qos2-helper.py'])
			pub.wait()
			# Should have now received a publish command
			publish_recvd = sock.recv(256)

			if publish_recvd != publish_packet:
				print "FAIL: Received publish not correct."
				print "Received: "+publish_recvd+" length="+str(len(publish_recvd))
				print "Expected: "+publish_packet+" length="+str(len(publish_packet))
				rc = 1
			else:
				# Wait for longer than 5 seconds to get republish with dup set
				# This is covered by the 8 second timeout
				publish_recvd = sock.recv(256)

				if publish_recvd != publish_dup_packet:
					print "FAIL: Recieved publish with dup not correct."
					print "Received: "+publish_recvd+" length="+str(len(publish_recvd))
					print "Expected: "+publish_packet+" length="+str(len(publish_packet))
					rc = 1
				else:
					sock.send(pubrec_packet)
					pubrel_recvd = sock.recv(256)

					if pubrel_recvd != pubrel_packet:
						(cmd, rl, mid) = unpack('!BBH', pubrel_recvd)
						print "FAIL: Expected 98,2,"+str(mid)+" got " + str(cmd) + "," + str(rl) + "," + str(mid)
						rc = 1
					else:
						# Wait for longer than 5 seconds to get republish with dup set
						# This is covered by the 8 second timeout
						pubrel_recvd = sock.recv(256)

						if pubrel_recvd != pubrel_dup_packet:
							(cmd, rl, mid) = unpack('!BBH', pubrel_recvd)
							print "FAIL: Expected 106,2,"+str(mid)+" got " + str(cmd) + "," + str(rl) + "," + str(mid)
							rc = 1
						else:
							sock.send(pubcomp_packet)

	sock.close()
finally:
	broker.terminate()

exit(rc)

