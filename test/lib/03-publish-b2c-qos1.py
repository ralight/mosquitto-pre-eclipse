#!/usr/bin/python

# Test whether a client responds correctly to a PUBLISH with QoS 1.

import os
import subprocess
import socket
import sys
import time
from struct import *

rc = 1
keepalive = 60
connect_packet = pack('!BBH6sBBHH17s', 16, 12+2+17,6,"MQIsdp",3,2,keepalive,17,"publish-qos1-test")
connack_packet = pack('!BBBB', 32, 2, 0, 0);

disconnect_packet = pack('!BB', 224, 0)

mid = 123
publish_packet = pack('!BBH16sH7s', 48+2, 2+16+2+7, 16, "pub/qos1/receive", mid, "message")
puback_packet = pack('!BBH', 64, 2, mid)

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

    if connect_recvd != connect_packet:
        print("FAIL: Received incorrect connect.")
        print("Received: "+connect_recvd+" length="+str(len(connect_recvd)))
        print("Expected: "+connect_packet+" length="+str(len(connect_packet)))
    else:
        conn.send(connack_packet)
        conn.send(publish_packet)
        puback_recvd = conn.recv(256)

        if puback_recvd != puback_packet:
            print("FAIL: Received incorrect puback.")
            print("Received: "+puback_recvd+" length="+str(len(puback_recvd)))
            print("Expected: "+puback_packet+" length="+str(len(puback_packet)))
        else:
            rc = 0

    conn.close()
finally:
    client.terminate()
    client.wait()
    sock.close()

exit(rc)
