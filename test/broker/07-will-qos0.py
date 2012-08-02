#!/usr/bin/python

# Test whether a client will is transmitted correctly.

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
mid = 53
keepalive = 60
connect_packet = pack('!BBH6sBBHH14s', 16, 12+2+14,6,"MQIsdp",3,2,keepalive,14,"will-qos0-test")
connack_packet = pack('!BBBB', 32, 2, 0, 0);

subscribe_packet = pack('!BBHH14sB', 130, 2+2+14+1, mid, 14, "will/qos0/test", 0)
suback_packet = pack('!BBHB', 144, 2+1, mid, 0)

publish_packet = pack('!BBH14s12s', 48, 2+14+12, 14, "will/qos0/test", "will-message")

broker = subprocess.Popen(['../../src/mosquitto', '-p', '1888'], stderr=subprocess.PIPE)

try:
    time.sleep(0.5)

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(30)
    sock.connect(("localhost", 1888))
    sock.send(connect_packet)
    connack_recvd = sock.recv(256)

    if mosq_test.packet_matches("connack", connack_recvd, connack_packet):
        sock.send(subscribe_packet)
        suback_recvd = sock.recv(256)

        if mosq_test.packet_matches("suback", suback_recvd, suback_packet):
            will = subprocess.Popen(['./07-will-qos0-helper.py'])
            will.wait()

            publish_recvd = sock.recv(256)

            if mosq_test.packet_matches("publish", publish_recvd, publish_packet):
                rc = 0

    sock.close()
finally:
    broker.terminate()
    broker.wait()

exit(rc)

