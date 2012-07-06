#!/usr/bin/python

# Test whether a client sends a correct SUBSCRIBE to a topic with QoS 1.

# The client should connect to port 1888 with keepalive=60, clean session set,
# and client id subscribe-qos1-test
# The test will send a CONNACK message to the client with rc=0. Upon receiving
# the CONNACK and verifying that rc=0, the client should send a SUBSCRIBE
# message to subscribe to topic "qos1/test" with QoS=1. If rc!=0, the client
# should exit with an error.
# Upon receiving the correct SUBSCRIBE message, the test will reply with a
# SUBACK message with the accepted QoS set to 1. On receiving the SUBACK
# message, the client should send a DISCONNECT message.

import os
import subprocess
import socket
import sys
import time
from struct import *

rc = 1
keepalive = 60
connect_packet = pack('!BBH6sBBHH19s', 16, 12+2+19,6,"MQIsdp",3,2,keepalive,19,"subscribe-qos1-test")
connack_packet = pack('!BBBB', 32, 2, 0, 0);

disconnect_packet = pack('!BB', 224, 0)

mid = 1
subscribe_packet = pack('!BBHH9sB', 130, 2+2+9+1, mid, 9, "qos1/test", 1)
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

    if connect_recvd != connect_packet:
        print("FAIL: Received incorrect connect.")
        print("Received: "+connect_recvd+" length="+str(len(connect_recvd)))
        print("Expected: "+connect_packet+" length="+str(len(connect_packet)))
    else:
        conn.send(connack_packet)
        subscribe_recvd = conn.recv(256)

        if subscribe_recvd != subscribe_packet:
            print("FAIL: Received incorrect subscribe.")
            print("Received: "+subscribe_recvd+" length="+str(len(subscribe_recvd)))
            print("Expected: "+subscribe_packet+" length="+str(len(subscribe_packet)))
        else:
            conn.send(suback_packet)
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
    sock.close()

exit(rc)
