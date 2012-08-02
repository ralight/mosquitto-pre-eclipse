#!/usr/bin/python

# Does a bridge resend a QoS=1 message correctly after a disconnect?

import os
import subprocess
import socket
import time
from struct import *

import inspect, os, sys
# From http://stackoverflow.com/questions/279237/python-import-a-module-from-a-folder
cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],"..")))
if cmd_subfolder not in sys.path:
    sys.path.insert(0, cmd_subfolder)

import mosq_test

rc = 1
keepalive = 60
client_id = socket.gethostname()+".bridge_sample"
clen = len(client_id)
connect_packet = pack('!BBH6sBBHH'+str(clen)+'s', 16, 12+2+clen,6,"MQIsdp",128+3,0,keepalive,clen,client_id)
connack_packet = pack('!BBBB', 32, 2, 0, 0);

mid = 1
subscribe_packet = pack('!BBHH8sB', 130, 2+2+8+1, mid, 8, "bridge/#", 1)
suback_packet = pack('!BBHB', 144, 2+1, mid, 1)

mid = 3
subscribe2_packet = pack('!BBHH8sB', 130, 2+2+8+1, mid, 8, "bridge/#", 1)
suback2_packet = pack('!BBHB', 144, 2+1, mid, 1)

mid = 2
publish_packet = pack('!BBH22sH18s', 48+2, 2+22+2+18, 22, "bridge/disconnect/test", mid, "disconnect-message")
publish_dup_packet = pack('!BBH22sH18s', 48+8+2, 2+22+2+18, 22, "bridge/disconnect/test", mid, "disconnect-message")
puback_packet = pack('!BBH', 64, 2, mid)

ssock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ssock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
ssock.settimeout(40)
ssock.bind(('', 1888))
ssock.listen(5)

broker = subprocess.Popen(['../../src/mosquitto', '-c', '06-bridge-br2b-disconnect-qos1.conf'], stderr=subprocess.PIPE)

try:
    time.sleep(0.5)

    (bridge, address) = ssock.accept()
    bridge.settimeout(10)
    connect_recvd = bridge.recv(256)

    if mosq_test.packet_matches("connect", connect_recvd, connect_packet):
        bridge.send(connack_packet)
        subscribe_recvd = bridge.recv(256)
        if mosq_test.packet_matches("subscribe", subscribe_recvd, subscribe_packet):
            bridge.send(suback_packet)

            pub = subprocess.Popen(['./06-bridge-br2b-disconnect-qos1-helper.py'])
            if pub.wait():
                exit(1)

            publish_recvd = bridge.recv(256)
            if mosq_test.packet_matches("publish", publish_recvd, publish_packet):
                bridge.close()

                (bridge, address) = ssock.accept()
                bridge.settimeout(10)
                connect_recvd = bridge.recv(256)

                if mosq_test.packet_matches("connect", connect_recvd, connect_packet):
                    bridge.send(connack_packet)
                    subscribe_recvd = bridge.recv(256)
                    if mosq_test.packet_matches("2nd subscribe", subscribe_recvd, subscribe2_packet):
                        bridge.send(suback2_packet)

                        publish_recvd = bridge.recv(256)
                        if mosq_test.packet_matches("2nd publish", publish_recvd, publish_dup_packet):
                            rc = 0

    bridge.close()
finally:
    try:
        bridge.close()
    except NameError:
        pass

    broker.terminate()
    broker.wait()
    ssock.close()

exit(rc)

