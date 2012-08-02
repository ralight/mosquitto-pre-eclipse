#!/usr/bin/python

# Test whether a SUBSCRIBE to a topic with QoS 2 results in the correct SUBACK packet.

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
mid = 3
keepalive = 60
connect_packet = pack('!BBH6sBBHH21s', 16, 12+2+21,6,"MQIsdp",3,2,keepalive,21,"unsubscribe-qos2-test")
connack_packet = pack('!BBBB', 32, 2, 0, 0);

unsubscribe_packet = pack('!BBHH9s', 162, 2+2+9, mid, 9, "qos2/test")
unsuback_packet = pack('!BBH', 176, 2, mid)

broker = subprocess.Popen(['../../src/mosquitto', '-p', '1888'], stderr=subprocess.PIPE)

try:
    time.sleep(0.5)

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(("localhost", 1888))
    sock.send(connect_packet)
    connack_recvd = sock.recv(256)

    if mosq_test.packet_matches("connack", connack_recvd, connack_packet):
        sock.send(unsubscribe_packet)
        unsuback_recvd = sock.recv(256)

        if mosq_test.packet_matches("unsuback", unsuback_recvd, unsuback_packet):
            rc = 0

    sock.close()
finally:
    broker.terminate()
    broker.wait()

exit(rc)

