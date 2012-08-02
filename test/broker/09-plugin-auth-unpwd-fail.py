#!/usr/bin/python

# Test whether a connection is successful with correct username and password
# when using a simple auth_plugin.

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
connect_packet = pack('!BBH6sBBHH22sH13sH5s', 16, 12+2+22+2+13+2+5,6,"MQIsdp",3,194,keepalive,22,"connect-uname-pwd-test",13,"test-username",5,"wrong")
connack_packet = pack('!BBBB', 32, 2, 0, 4);

broker = subprocess.Popen(['../../src/mosquitto', '-c', '09-plugin-auth-unpwd-fail.conf'], stderr=subprocess.PIPE)

try:
    time.sleep(0.5)

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(10)
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

