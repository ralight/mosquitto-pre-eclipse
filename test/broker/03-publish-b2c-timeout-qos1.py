#!/usr/bin/python

# Test whether a SUBSCRIBE to a topic with QoS 2 results in the correct SUBACK packet.

import subprocess
import socket
import time
from struct import *
from os import environ

import inspect, os, sys
# From http://stackoverflow.com/questions/279237/python-import-a-module-from-a-folder
cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],"..")))
if cmd_subfolder not in sys.path:
    sys.path.insert(0, cmd_subfolder)

import mosq_test

rc = 1
mid = 3265
keepalive = 60
connect_packet = pack('!BBH6sBBHH21s', 16, 12+2+21,6,"MQIsdp",3,2,keepalive,21,"pub-qos1-timeout-test")
connack_packet = pack('!BBBB', 32, 2, 0, 0);

subscribe_packet = pack('!BBHH17sB', 130, 2+2+17+1, mid, 17, "qos1/timeout/test", 1)
suback_packet = pack('!BBHB', 144, 2+1, mid, 1)

mid = 1
publish_packet = pack('!BBH17sH15s', 48+2, 2+17+2+15, 17, "qos1/timeout/test", mid, "timeout-message")
publish_dup_packet = pack('!BBH17sH15s', 48+8+2, 2+17+2+15, 17, "qos1/timeout/test", mid, "timeout-message")
puback_packet = pack('!BBH', 64, 2, mid)

broker = subprocess.Popen(['../../src/mosquitto', '-c', '03-publish-b2c-timeout-qos1.conf'], stderr=subprocess.PIPE)

try:
    time.sleep(0.5)

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(60) # 60 seconds timeout is much longer than 5 seconds message retry.
    sock.connect(("localhost", 1888))
    sock.send(connect_packet)
    connack_recvd = sock.recv(256)

    if mosq_test.packet_matches("connack", connack_recvd, connack_packet):
        sock.send(subscribe_packet)
        suback_recvd = sock.recv(256)

        if mosq_test.packet_matches("suback", suback_recvd, suback_packet):
            pub = subprocess.Popen(['./03-publish-b2c-timeout-qos1-helper.py'])
            pub.wait()
            # Should have now received a publish command
            publish_recvd = sock.recv(256)

            if mosq_test.packet_matches("publish", publish_recvd, publish_packet):
                # Wait for longer than 5 seconds to get republish with dup set
                # This is covered by the 8 second timeout
                publish_recvd = sock.recv(256)

                if mosq_test.packet_matches("dup publish", publish_recvd, publish_dup_packet):
                    sock.send(puback_packet)
                    rc = 0

    sock.close()
finally:
    broker.terminate()
    broker.wait()

exit(rc)

