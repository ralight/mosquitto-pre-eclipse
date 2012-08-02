#!/usr/bin/python

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
connect_packet = pack('!BBH6sBBHH11s', 16, 12+2+11,6,"MQIsdp",3,2,keepalive,11,"test-helper")
connack_packet = pack('!BBBB', 32, 2, 0, 0);

publish_packet = pack('!BBH16s24s', 48, 2+16+24, 16, "bridge/reconnect", "bridge-reconnect-message")

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(("localhost", 1889))
sock.send(connect_packet)
connack_recvd = sock.recv(256)

if mosq_test.packet_matches("connack", connack_recvd, connack_packet):
    sock.send(publish_packet)
    rc = 0

sock.close()
    
exit(rc)

