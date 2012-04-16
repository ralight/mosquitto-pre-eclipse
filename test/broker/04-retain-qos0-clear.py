#!/usr/bin/python

# Test whether a retained PUBLISH is cleared when a zero length retained
# message is published to a topic.

import subprocess
import socket
import time
from struct import *

rc = 1
keepalive = 60
connect_packet = pack('!BBH6sBBHH17s', 16, 12+2+17,6,"MQIsdp",3,2,keepalive,17,"retain-clear-test")
connack_packet = pack('!BBBB', 32, 2, 0, 0);

publish_packet = pack('!BBH17s17s', 48+1, 2+17+17, 17, "retain/clear/test", "retained message")
retain_clear_packet = pack('!BBH17s', 48+1, 2+17, 17, "retain/clear/test")
mid_sub = 592
subscribe_packet = pack('!BBHH17sB', 130, 2+2+17+1, mid_sub, 17, "retain/clear/test", 0)
suback_packet = pack('!BBHB', 144, 2+1, mid_sub, 0)

mid_unsub = 593
unsubscribe_packet = pack('!BBHH17s', 162, 2+2+17, mid_unsub, 17, "retain/clear/test")
unsuback_packet = pack('!BBH', 176, 2, mid_unsub)

broker = subprocess.Popen(['../../src/mosquitto', '-p', '1888'], stderr=subprocess.PIPE)

try:
	time.sleep(0.1)

	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.settimeout(4) # Reduce timeout for when we don't expect incoming data.
	sock.connect(("localhost", 1888))
	sock.send(connect_packet)
	connack_recvd = sock.recv(256)

	if connack_recvd != connack_packet:
		print("FAIL: Connect failed.")
	else:
		# Send retained message
		sock.send(publish_packet)
		# Subscribe to topic, we should get the retained message back.
		sock.send(subscribe_packet)
		suback_recvd = sock.recv(256)

		if suback_recvd != suback_packet:
			(cmd, rl, mid_recvd, qos) = unpack('!BBHB', suback_recvd)
			print("FAIL: Expected 144,3,"+str(mid_sub)+",0 got " + str(cmd) + "," + str(rl) + "," + str(mid_recvd) + "," + str(qos))
		else:
			publish_recvd = sock.recv(256)

			if publish_recvd != publish_packet:
				print("FAIL: Recieved incorrect publish.")
				print("Received: "+publish_recvd+" length="+str(len(publish_recvd)))
				print("Expected: "+publish_packet+" length="+str(len(publish_packet)))
			else:
				# Now unsubscribe from the topic before we clear the retained
				# message.
				sock.send(unsubscribe_packet)
				unsuback_recvd = sock.recv(256)

				if unsuback_recvd != unsuback_packet:
					(cmd, rl, mid_recvd) = unpack('!BBH', unsuback_recvd)
					print("FAIL: Expected 176,2,"+str(mid_unsub)+",0 got " + str(cmd) + "," + str(rl) + "," + str(mid_recvd))
				else:
					# Now clear the retained message.
					sock.send(retain_clear_packet)

					# Subscribe to topic, we shouldn't get anything back apart
					# from the SUBACK.
					sock.send(subscribe_packet)
					suback_recvd = sock.recv(256)
					if suback_recvd != suback_packet:
						(cmd, rl, mid_recvd, qos) = unpack('!BBHB', suback_recvd)
						print("FAIL: Expected 144,3,"+str(mid_sub)+",0 got " + str(cmd) + "," + str(rl) + "," + str(mid_recvd) + "," + str(qos))
					else:
						try:
							retain_clear = sock.recv(256)
						except socket.timeout:
							# This is the expected event
							rc = 0
						else:
							print("FAIL: Received unexpected message.")

	sock.close()
finally:
	broker.terminate()

exit(rc)

