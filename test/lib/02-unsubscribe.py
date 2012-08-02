#!/usr/bin/python

# Test whether a client sends a correct UNSUBSCRIBE packet.

import os
import subprocess
import socket
import sys
import time
from struct import *

import mosq_test

rc = 1
keepalive = 60
connect_packet = pack('!BBH6sBBHH16s', 16, 12+2+16,6,"MQIsdp",3,2,keepalive,16,"unsubscribe-test")
connack_packet = pack('!BBBB', 32, 2, 0, 0);

disconnect_packet = pack('!BB', 224, 0)

mid = 1
unsubscribe_packet = pack('!BBHH16s', 162, 2+2+16, mid, 16, "unsubscribe/test")
unsuback_packet = pack('!BBH', 176, 2, mid)

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
        unsubscribe_recvd = conn.recv(256)

        if mosq_test.packet_matches("unsubscribe", unsubscribe_recvd, unsubscribe_packet):
            conn.send(unsuback_packet)
            disconnect_recvd = conn.recv(256)
        
            if mosq_test.packet_matches("disconnect", disconnect_recvd, disconnect_packet):
                rc = 0
        
    conn.close()
finally:
    client.terminate()
    client.wait()
    sock.close()

exit(rc)
