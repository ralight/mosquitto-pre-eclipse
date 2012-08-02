#!/usr/bin/python

# Test whether a retained PUBLISH to a topic with QoS 0 is actually retained.

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
mid = 16
connect_packet = pack('!BBH6sBBHH16s', 16, 12+2+16,6,"MQIsdp",3,2,keepalive,16,"retain-qos0-test")
connack_packet = pack('!BBBB', 32, 2, 0, 0);

publish_packet = pack('!BBH16s16s', 48+1, 2+16+16, 16, "retain/qos0/test", "retained message")
subscribe_packet = pack('!BBHH16sB', 130, 2+2+16+1, mid, 16, "retain/qos0/test", 0)
suback_packet = pack('!BBHB', 144, 2+1, mid, 0)

broker = subprocess.Popen(['../../src/mosquitto', '-p', '1888'], stderr=subprocess.PIPE)

try:
    time.sleep(0.5)

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(("localhost", 1888))
    sock.send(connect_packet)
    connack_recvd = sock.recv(256)

    if mosq_test.packet_matches("connack", connack_recvd, connack_packet):
        sock.send(publish_packet)
        sock.send(subscribe_packet)

        suback_recvd = sock.recv(256)

        if mosq_test.packet_matches("suback", suback_recvd, suback_packet):
            publish_recvd = sock.recv(256)

            if mosq_test.packet_matches("publish", publish_recvd, publish_packet):
                rc = 0
    sock.close()
finally:
    broker.terminate()
    broker.wait()

exit(rc)

