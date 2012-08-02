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
connect_packet = pack('!BBH6sBBHH16s', 16, 12+2+16,6,"MQIsdp",3,2,keepalive,16,"subpub-qos2-test")
connack_packet = pack('!BBBB', 32, 2, 0, 0);

subscribe_packet = pack('!BBHH11sB', 130, 2+2+11+1, mid, 11, "subpub/qos2", 2)
suback_packet = pack('!BBHB', 144, 2+1, mid, 2)

mid = 301
publish_packet = pack('!BBH11sH7s', 48+4, 2+11+2+7, 11, "subpub/qos2", mid, "message")
pubrec_packet = pack('!BBH', 80, 2, mid)
pubrel_packet = pack('!BBH', 96+2, 2, mid)
pubcomp_packet = pack('!BBH', 112, 2, mid)

mid = 1
publish_packet2 = pack('!BBH11sH7s', 48+4, 2+11+2+7, 11, "subpub/qos2", mid, "message")
pubrec_packet2 = pack('!BBH', 80, 2, mid)
pubrel_packet2 = pack('!BBH', 96+2, 2, mid)
pubcomp_packet2 = pack('!BBH', 112, 2, mid)

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
            pubrec_recvd = sock.recv(256)

            if mosq_test.packet_matches("pubrec", pubrec_recvd, pubrec_packet):
                sock.send(pubrel_packet)
                pubcomp_recvd = sock.recv(256)

                if mosq_test.packet_matches("pubcomp", pubcomp_recvd, pubcomp_packet):
                    publish_recvd = sock.recv(256)

                    if mosq_test.packet_matches("publish2", publish_recvd, publish_packet2):
                        sock.send(pubrec_packet2)
                        pubrel_recvd = sock.recv(256)

                        if mosq_test.packet_matches("pubrel2", pubrel_recvd, pubrel_packet2):
                            # Broker side of flow complete so can quit here.
                            rc = 0

    sock.close()
finally:
    broker.terminate()
    broker.wait()

exit(rc)

