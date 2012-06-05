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
connect_packet = pack('!BBH6sBBHH17s', 16, 12+2+17,6,"MQIsdp",3,2,keepalive,17,"publish-qos2-test")
connack_packet = pack('!BBBB', 32, 2, 0, 0);

disconnect_packet = pack('!BB', 224, 0)

mid = 13423
publish_packet = pack('!BBH16sH7s', 48+4, 2+16+2+7, 16, "pub/qos2/receive", mid, "message")
pubrec_packet = pack('!BBH', 80, 2, mid)
pubrel_packet = pack('!BBH', 96, 2, mid)
pubcomp_packet = pack('!BBH', 112, 2, mid)

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.settimeout(5)
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
        pubrec_recvd = conn.recv(256)

        if pubrec_recvd != pubrec_packet:
            print("FAIL: Received incorrect pubrec.")
            print("Received: "+pubrec_recvd+" length="+str(len(pubrec_recvd)))
            print("Expected: "+pubrec_packet+" length="+str(len(pubrec_packet)))
        else:
            # Should be repeated due to timeout
            pubrec_recvd = conn.recv(256)
            if pubrec_recvd != pubrec_packet:
                print("FAIL: Received incorrect pubrec.")
                print("Received: "+pubrec_recvd+" length="+str(len(pubrec_recvd)))
                print("Expected: "+pubrec_packet+" length="+str(len(pubrec_packet)))
            else:
                conn.send(pubrel_packet)
                pubcomp_recvd = conn.recv(256)
                if pubcomp_recvd != pubcomp_packet:
                    print("FAIL: Received incorrect pubcomp.")
                    print("Received: "+pubcomp_recvd+" length="+str(len(pubcomp_recvd)))
                    print("Expected: "+pubcomp_packet+" length="+str(len(pubcomp_packet)))
                else:
                    rc = 0

    conn.close()
finally:
    for i in range(0, 5):
        if client.returncode != None:
            break
        time.sleep(0.1)

    client.terminate()
    client.wait()
    sock.close()
    if client.returncode != 0:
        exit(1)

exit(rc)
