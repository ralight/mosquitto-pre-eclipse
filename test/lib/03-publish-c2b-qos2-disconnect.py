#!/usr/bin/python

# Test whether a client sends a correct PUBLISH to a topic with QoS 1 and responds to a disconnect.

import inspect
import os
import subprocess
import socket
import sys
import time
from struct import *

# From http://stackoverflow.com/questions/279237/python-import-a-module-from-a-folder
cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],"..")))
if cmd_subfolder not in sys.path:
    sys.path.insert(0, cmd_subfolder)

import mosq_test

rc = 1
keepalive = 60
connect_packet = pack('!BBH6sBBHH17s', 16, 12+2+17,6,"MQIsdp",3,2,keepalive,17,"publish-qos2-test")
connack_packet = pack('!BBBB', 32, 2, 0, 0);

disconnect_packet = pack('!BB', 224, 0)

mid = 1
publish_packet = pack('!BBH13sH7s', 48+4, 2+13+2+7, 13, "pub/qos2/test", mid, "message")
publish_dup_packet = pack('!BBH13sH7s', 48+8+4, 2+13+2+7, 13, "pub/qos2/test", mid, "message")
pubrec_packet = pack('!BBH', 80, 2, mid)
pubrel_packet = pack('!BBH', 96+2, 2, mid)
pubrel_dup_packet = pack('!BBH', 96+8+2, 2, mid)
pubcomp_packet = pack('!BBH', 112, 2, mid)

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
    conn.settimeout(5)
    connect_recvd = conn.recv(256)

    if mosq_test.packet_matches("connect", connect_recvd, connect_packet):
        conn.send(connack_packet)
        publish_recvd = conn.recv(256)

        if mosq_test.packet_matches("publish", publish_recvd, publish_packet):
            # Disconnect client. It should reconnect.
            conn.close()

            (conn, address) = sock.accept()
            conn.settimeout(5)
            connect_recvd = conn.recv(256)

            if mosq_test.packet_matches("connect", connect_recvd, connect_packet):
                conn.send(connack_packet)
                publish_recvd = conn.recv(256)

                if mosq_test.packet_matches("retried publish", publish_recvd, publish_dup_packet):
                    conn.send(pubrec_packet)
                    pubrel_recvd = conn.recv(256)

                    if mosq_test.packet_matches("pubrel", pubrel_recvd, pubrel_packet):
                        # Disconnect client. It should reconnect.
                        conn.close()

                        (conn, address) = sock.accept()
                        conn.settimeout(5)
                        connect_recvd = conn.recv(256)

                        # Complete connection and message flow.
                        if mosq_test.packet_matches("connect", connect_recvd, connect_packet):
                            conn.send(connack_packet)

                            publish_recvd = conn.recv(256)
                            if mosq_test.packet_matches("2nd retried publish", publish_recvd, publish_dup_packet):
                                conn.send(pubrec_packet)
                                pubrel_recvd = conn.recv(256)

                                if mosq_test.packet_matches("pubrel", pubrel_recvd, pubrel_packet):
                                    conn.send(pubcomp_packet)
                                    disconnect_recvd = conn.recv(256)

                                    if mosq_test.packet_matches("disconnect", disconnect_recvd, disconnect_packet):
                                        rc = 0

    conn.close()
finally:
    client.terminate()
    client.wait()
    sock.close()

exit(rc)
