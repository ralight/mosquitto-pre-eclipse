#!/usr/bin/python

# Test whether a client sends a correct SUBSCRIBE to a topic with QoS 2.

# The client should connect to port 1888 with keepalive=60, clean session set,
# and client id subscribe-qos2-test
# The test will send a CONNACK message to the client with rc=0. Upon receiving
# the CONNACK and verifying that rc=0, the client should send a SUBSCRIBE
# message to subscribe to topic "qos2/test" with QoS=2. If rc!=0, the client
# should exit with an error.
# Upon receiving the correct SUBSCRIBE message, the test will reply with a
# SUBACK message with the accepted QoS set to 2. On receiving the SUBACK
# message, the client should send a DISCONNECT message.

import os
import subprocess
import socket
import sys
import time
from struct import *

import mosq_test

rc = 1
keepalive = 60
connect_packet = pack('!BBH6sBBHH19s', 16, 12+2+19,6,"MQIsdp",3,2,keepalive,19,"subscribe-qos2-test")
connack_packet = pack('!BBBB', 32, 2, 0, 0);

disconnect_packet = pack('!BB', 224, 0)

mid = 1
subscribe_packet = pack('!BBHH9sB', 130, 2+2+9+1, mid, 9, "qos2/test", 2)
suback_packet = pack('!BBHB', 144, 2+1, mid, 0)

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.settimeout(10)
sock.bind(('', 1888))
sock.listen(5)

client_args = sys.argv[1:]
env = dict(os.environ)
env['LD_LIBRARY_PATH'] = '../../lib:../../lib/cpp'
try:
    pp = env['PYTHONPATH']
except KeyError:
    pp = ''
env['PYTHONPATH'] = '../../lib/python:'+pp
client = subprocess.Popen(client_args, env=env)

try:
    (conn, address) = sock.accept()
    conn.settimeout(10)
    connect_recvd = conn.recv(256)

    if mosq_test.packet_matches("connect", connect_recvd, connect_packet):
        conn.send(connack_packet)
        subscribe_recvd = conn.recv(256)

        if mosq_test.packet_matches("subscribe", subscribe_recvd, subscribe_packet):
            conn.send(suback_packet)
            disconnect_recvd = conn.recv(256)
        
            if mosq_test.packet_matches("disconnect", disconnect_recvd, disconnect_packet):
                rc = 0
        
    conn.close()
finally:
    client.terminate()
    client.wait()
    sock.close()

exit(rc)
