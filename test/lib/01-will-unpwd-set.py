#!/usr/bin/python

# Test whether a client produces a correct connect with a will, username and password.

import os
import subprocess
import socket
import sys
import time
from struct import *

rc = 1
keepalive = 60
connect_packet = pack('!BBH6sBBHH17sH10sH12sH8sH16s', 16,
        12+2+17+2+10+2+12+2+8+2+16,6,"MQIsdp",3,2+4+16+64+128,keepalive,17,"01-will-unpwd-set",10,"will-topic",12,
        "will message",8,"oibvvwqw",16,"#'^2hg9a&nm38*us")

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
        rc = 0

    conn.close()
finally:
    client.terminate()
    client.wait()
    sock.close()

exit(rc)

