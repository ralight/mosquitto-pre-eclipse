#!/usr/bin/python

# Test whether a client subscribed to a topic receives its own message sent to that topic.

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
mid = 530
keepalive = 60
connect_packet = pack('!BBH6sBBHH16s', 16, 12+2+16,6,"MQIsdp",3,2,keepalive,16,"subpub-qos1-test")
connack_packet = pack('!BBBB', 32, 2, 0, 0);

subscribe_packet = pack('!BBHH11sB', 130, 2+2+11+1, mid, 11, "subpub/qos1", 1)
suback_packet = pack('!BBHB', 144, 2+1, mid, 1)

mid = 300
publish_packet = pack('!BBH11sH7s', 48+2, 2+11+2+7, 11, "subpub/qos1", mid, "message")
puback_packet = pack('!BBH', 64, 2, mid)

mid = 1
publish_packet2 = pack('!BBH11sH7s', 48+2, 2+11+2+7, 11, "subpub/qos1", mid, "message")

broker = subprocess.Popen(['../../src/mosquitto', '-p', '1888'], stderr=subprocess.PIPE)

try:
    time.sleep(0.5)

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(10)
    sock.connect(("localhost", 1888))
    sock.send(connect_packet)
    connack_recvd = sock.recv(256)

    if mosq_test.packet_matches("connack", connack_recvd, connack_packet):
        sock.send(subscribe_packet)
        suback_recvd = sock.recv(256)

        if mosq_test.packet_matches("suback", suback_recvd, suback_packet):
            sock.send(publish_packet)
            puback_recvd = sock.recv(256)

            if mosq_test.packet_matches("puback", puback_recvd, puback_packet):
                publish_recvd = sock.recv(256)

                if mosq_test.packet_matches("publish2", publish_recvd, publish_packet2):
                    rc = 0

    sock.close()
finally:
    broker.terminate()
    broker.wait()

exit(rc)

