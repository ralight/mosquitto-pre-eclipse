#!/usr/bin/python

# Test whether a client produces a correct connect and subsequent disconnect when using SSL.

# The client should connect to port 1888 with keepalive=60, clean session set,
# and client id 08-ssl-connect-no-auth
# It should use the CA certificate ssl/test-ca.crt for verifying the server.
# The test will send a CONNACK message to the client with rc=0. Upon receiving
# the CONNACK and verifying that rc=0, the client should send a DISCONNECT
# message. If rc!=0, the client should exit with an error.

import os
import subprocess
import socket
import ssl
import sys
import time
from struct import *

if sys.version < '2.7':
    print("WARNING: SSL not supported on Python 2.6")
    exit(0)

rc = 1
keepalive = 60
connect_packet = pack('!BBH6sBBHH22s', 16, 12+2+22,6,"MQIsdp",3,2,keepalive,22,"08-ssl-connect-no-auth")
connack_packet = pack('!BBBB', 32, 2, 0, 0);
disconnect_packet = pack('!BB', 224, 0)

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
ssock = ssl.wrap_socket(sock, ca_certs="../ssl/test-ca.crt", keyfile="../ssl/server.key", certfile="../ssl/server.crt", server_side=True, ssl_version=ssl.PROTOCOL_TLSv1)
ssock.settimeout(10)
ssock.bind(('', 1888))
ssock.listen(5)

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
    (conn, address) = ssock.accept()
    conn.settimeout(10)
    connect_recvd = conn.recv(256)

    if connect_recvd != connect_packet:
        print("FAIL: Received incorrect connect.")
        print("Received: "+connect_recvd+" length="+str(len(connect_recvd)))
        print("Expected: "+connect_packet+" length="+str(len(connect_packet)))
    else:
        conn.send(connack_packet)
        disconnect_recvd = conn.recv(256)

        if disconnect_recvd != disconnect_packet:
            print("FAIL: Received incorrect disconnect.")
            (cmd, rl) = unpack('!BB', disconnect_recvd)
            print("Received: "+str(cmd)+", " + str(rl))
            print("Expected: 224, 0")
        else:
            rc = 0

    conn.close()
finally:
    client.terminate()
    client.wait()
    ssock.close()

exit(rc)
