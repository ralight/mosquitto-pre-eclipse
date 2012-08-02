#!/usr/bin/python

# Test whether a connection is denied if it provides just a username when it
# needs a username and password.

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
keepalive = 10
connect_packet = pack('!BBH6sBBHH18sH4s', 16, 12+2+18+2+4,6,"MQIsdp",3,130,keepalive,18,"connect-uname-test",4,"user")
connack_packet = pack('!BBBB', 32, 2, 0, 4);

broker = subprocess.Popen(['../../src/mosquitto', '-c', '01-connect-uname-no-password-denied.conf'], stderr=subprocess.PIPE)

try:
    time.sleep(0.5)

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(("localhost", 1888))
    sock.send(connect_packet)
    connack_recvd = sock.recv(256)
    sock.close()

    if mosq_test.packet_matches("connack", connack_recvd, connack_packet):
        rc = 0
finally:
    broker.terminate()
    broker.wait()

exit(rc)

