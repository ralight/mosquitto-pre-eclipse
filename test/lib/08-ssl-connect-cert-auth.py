#!/usr/bin/python

# Test whether a client produces a correct connect and subsequent disconnect when using SSL.
# Client must provide a certificate.

# The client should connect to port 1888 with keepalive=60, clean session set,
# and client id 08-ssl-connect-crt-auth
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

import mosq_test

if sys.version < '2.7':
    print("WARNING: SSL not supported on Python 2.6")
    exit(0)

rc = 1
keepalive = 60
connect_packet = pack('!BBH6sBBHH23s', 16, 12+2+23,6,"MQIsdp",3,2,keepalive,23,"08-ssl-connect-crt-auth")
connack_packet = pack('!BBBB', 32, 2, 0, 0);
disconnect_packet = pack('!BB', 224, 0)

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
ssock = ssl.wrap_socket(sock, ca_certs="../ssl/test-ca.crt",
        keyfile="../ssl/server.key", certfile="../ssl/server.crt",
        server_side=True, ssl_version=ssl.PROTOCOL_TLSv1, cert_reqs=ssl.CERT_REQUIRED)
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

    if mosq_test.packet_matches("connect", connect_recvd, connect_packet):
        conn.send(connack_packet)
        disconnect_recvd = conn.recv(256)

        if mosq_test.packet_matches("disconnect", disconnect_recvd, disconnect_packet):
            rc = 0

    conn.close()
finally:
    client.terminate()
    client.wait()
    ssock.close()

exit(rc)
