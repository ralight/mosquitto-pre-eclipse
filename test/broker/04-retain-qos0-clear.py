#!/usr/bin/python

# Test whether a retained PUBLISH is cleared when a zero length retained
# message is published to a topic.

import subprocess
import socket
import time
from struct import *

import inspect, os, sys
# From http://stackoverflow.com/questions/279237/python-import-a-module-from-a-folder
cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],"..")))
if cmd_subfolder not in sys.path:
    sys.path.insert(0, cmd_subfolder)

import mosq_test

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
    time.sleep(0.5)

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(4) # Reduce timeout for when we don't expect incoming data.
    sock.connect(("localhost", 1888))
    sock.send(connect_packet)
    connack_recvd = sock.recv(256)

    if mosq_test.packet_matches("connack", connack_recvd, connack_packet):
        # Send retained message
        sock.send(publish_packet)
        # Subscribe to topic, we should get the retained message back.
        sock.send(subscribe_packet)
        suback_recvd = sock.recv(256)

        if mosq_test.packet_matches("suback", suback_recvd, suback_packet):
            publish_recvd = sock.recv(256)

            if mosq_test.packet_matches("publish", publish_recvd, publish_packet):
                # Now unsubscribe from the topic before we clear the retained
                # message.
                sock.send(unsubscribe_packet)
                unsuback_recvd = sock.recv(256)

                if mosq_test.packet_matches("unsuback", unsuback_recvd, unsuback_packet):
                    # Now clear the retained message.
                    sock.send(retain_clear_packet)

                    # Subscribe to topic, we shouldn't get anything back apart
                    # from the SUBACK.
                    sock.send(subscribe_packet)
                    suback_recvd = sock.recv(256)
                    if mosq_test.packet_matches("suback", suback_recvd, suback_packet):
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
    broker.wait()

exit(rc)

