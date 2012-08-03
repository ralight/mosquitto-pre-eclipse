#!/usr/bin/python

# Test whether a retained PUBLISH to a topic with QoS 1 is retained.
# Subscription is made with QoS 0 so the retained message should also have QoS
# 0.

import subprocess
import socket
import time

import inspect, os, sys
# From http://stackoverflow.com/questions/279237/python-import-a-module-from-a-folder
cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],"..")))
if cmd_subfolder not in sys.path:
    sys.path.insert(0, cmd_subfolder)

import mosq_test

rc = 1
keepalive = 60
connect_packet = mosq_test.gen_connect("retain-qos1-test", keepalive=keepalive)
connack_packet = mosq_test.gen_connack(rc=0)

mid = 6
publish_packet = mosq_test.gen_publish("retain/qos1/test", qos=1, mid=mid, payload="retained message", retain=True)
puback_packet = mosq_test.gen_puback(mid)
mid = 18
subscribe_packet = mosq_test.gen_subscribe(mid, "retain/qos1/test", 0)
suback_packet = mosq_test.gen_suback(mid, 0)
publish0_packet = mosq_test.gen_publish("retain/qos1/test", qos=0, payload="retained message", retain=True)

broker = subprocess.Popen(['../../src/mosquitto', '-p', '1888'], stderr=subprocess.PIPE)

try:
    time.sleep(0.5)

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(("localhost", 1888))
    sock.send(connect_packet)
    connack_recvd = sock.recv(len(connack_packet))

    if mosq_test.packet_matches("connack", connack_recvd, connack_packet):
        sock.send(publish_packet)
        puback_recvd = sock.recv(len(puback_packet))

        if mosq_test.packet_matches("puback", puback_recvd, puback_packet):
            sock.send(subscribe_packet)
            suback_recvd = sock.recv(len(suback_packet))

            if mosq_test.packet_matches("suback", suback_recvd, suback_packet):
                publish_recvd = sock.recv(len(publish0_packet))

                if mosq_test.packet_matches("publish0", publish_recvd, publish0_packet):
                    rc = 0
    sock.close()
finally:
    broker.terminate()
    broker.wait()

exit(rc)

