#!/usr/bin/python

# Test whether a client produces a correct connect and subsequent disconnect.

import os
import subprocess
import socket
import sys
import time
from struct import *

rc = 1
keepalive = 60
connect_packet = pack('!BBH6sBBHH21s', 16, 12+2+21,6,"MQIsdp",3,2,keepalive,21,"01-con-discon-success")
connack_packet = pack('!BBBB', 32, 2, 0, 0);


sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind(('', 1888))
sock.listen(5)

client_args = sys.argv[1:]
env = dict(os.environ)
env['LD_LIBRARY_PATH'] = '../../lib:../../lib/cpp'
client = subprocess.Popen(client_args, env=env)

try:
    (conn, address) = sock.accept()
    connect_recvd = conn.recv(256)

    if connect_recvd != connect_packet:
        print("FAIL: Received incorrect connect.")
        print("Received: "+connect_recvd+" length="+str(len(connect_recvd)))
        print("Expected: "+connect_packet+" length="+str(len(connect_packet)))
    else:
        rc = 0
finally:
    client.terminate()
    client.wait()

exit(rc)

