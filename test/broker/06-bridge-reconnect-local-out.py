#!/usr/bin/python

# Test whether a bridge topics work correctly after reconnection.
# Important point here is that persistence is enabled.

import os
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
connect_packet = pack('!BBH6sBBHH21s', 16, 12+2+21,6,"MQIsdp",3,2,keepalive,21,"bridge-reconnect-test")
connack_packet = pack('!BBBB', 32, 2, 0, 0);

mid = 180
subscribe_packet = pack('!BBHH8sB', 130, 2+2+8+1, mid, 8, "bridge/#", 0)
suback_packet = pack('!BBHB', 144, 2+1, mid, 0)
publish_packet = pack('!BBH16s24s', 48, 2+16+24, 16, "bridge/reconnect", "bridge-reconnect-message")

try:
    os.remove('mosquitto.db')
except OSError:
    pass

broker = subprocess.Popen(['../../src/mosquitto', '-p', '1888'], stderr=subprocess.PIPE)
time.sleep(0.5)
local_broker = subprocess.Popen(['../../src/mosquitto', '-c', '06-bridge-reconnect-local-out.conf'], stderr=subprocess.PIPE)
time.sleep(0.5)
local_broker.terminate()
local_broker.wait()
local_broker = subprocess.Popen(['../../src/mosquitto', '-c', '06-bridge-reconnect-local-out.conf'], stderr=subprocess.PIPE)

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
            sock.send(subscribe_packet)
            suback_recvd = sock.recv(256)

            if mosq_test.packet_matches("suback", suback_recvd, suback_packet):
                pub = subprocess.Popen(['./06-bridge-reconnect-local-out-helper.py'])
                pub.wait()
                # Should have now received a publish command
                publish_recvd = sock.recv(256)

                if mosq_test.packet_matches("publish", publish_recvd, publish_packet):
                    rc = 0
    sock.close()
finally:
    broker.terminate()
    broker.wait()
    local_broker.terminate()
    local_broker.wait()
    try:
        os.remove('mosquitto.db')
    except OSError:
        pass

exit(rc)

