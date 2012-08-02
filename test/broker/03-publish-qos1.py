#!/usr/bin/python

# Test whether a PUBLISH to a topic with QoS 1 results in the correct PUBACK packet.

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
mid = 19
keepalive = 60
connect_packet = pack('!BBH6sBBHH13s', 16, 12+2+13,6,"MQIsdp",3,2,keepalive,13,"pub-qos1-test")
connack_packet = pack('!BBBB', 32, 2, 0, 0);

publish_packet = pack('!BBH13sH7s', 48+2, 2+13+2+7, 13, "pub/qos1/test", mid, "message")
puback_packet = pack('!BBH', 64, 2, mid)

broker = subprocess.Popen(['../../src/mosquitto', '-p', '1888'], stderr=subprocess.PIPE)

try:
    time.sleep(0.5)

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(("localhost", 1888))
    sock.send(connect_packet)
    connack_recvd = sock.recv(256)

    if mosq_test.packet_matches("connack", connack_recvd, connack_packet):
        sock.send(publish_packet)
        puback_recvd = sock.recv(256)

        if mosq_test.packet_matches("puback", puback_recvd, puback_packet):
            rc = 0

    sock.close()
finally:
    broker.terminate()
    broker.wait()

exit(rc)

