#!/usr/bin/python

# Test whether a clean session client has a QoS 1 message queued for it.

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
mid = 109
keepalive = 60
connect_packet = pack('!BBH6sBBHH15s', 16, 12+2+15,6,"MQIsdp",3,0,keepalive,15,"clean-qos2-test")
connack_packet = pack('!BBBB', 32, 2, 0, 0);

disconnect_packet = pack('!BB', 224, 0,)

subscribe_packet = pack('!BBHH23sB', 130, 2+2+23+1, mid, 23, "qos1/clean_session/test", 1)
suback_packet = pack('!BBHB', 144, 2+1, mid, 1)

mid = 1
publish_packet = pack('!BBH23sH21s', 48+2, 2+23+2+21, 23, "qos1/clean_session/test", mid, "clean-session-message")
puback_packet = pack('!BBH', 64, 2, mid)

broker = subprocess.Popen(['../../src/mosquitto', '-p', '1888'], stderr=subprocess.PIPE)

try:
    time.sleep(0.5)

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(("localhost", 1888))
    sock.send(connect_packet)
    connack_recvd = sock.recv(256)

    if mosq_test.packet_matches("connack", connack_recvd, connack_packet):
        sock.send(subscribe_packet)
        suback_recvd = sock.recv(256)

        if mosq_test.packet_matches("suback", suback_recvd, suback_packet):
            sock.send(disconnect_packet)
            sock.close()

            pub = subprocess.Popen(['./05-clean-session-qos1-helper.py'])
            pub.wait()

            # Now reconnect and expect a publish message.
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(30)
            sock.connect(("localhost", 1888))
            sock.send(connect_packet)
            connack_recvd = sock.recv(256)

            if mosq_test.packet_matches("connack", connack_recvd, connack_packet):
                publish_recvd = sock.recv(256)

                if mosq_test.packet_matches("publish", publish_recvd, publish_packet):
                    sock.send(puback_packet)
                    rc = 0

    sock.close()
finally:
    broker.terminate()
    broker.wait()

exit(rc)

