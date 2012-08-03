#!/usr/bin/python

# Test whether a client subscribed to a topic receives its own message sent to that topic.

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
mid = 530
keepalive = 60
connect_packet = mosq_test.gen_connect("subpub-qos2-test", keepalive=keepalive)
connack_packet = mosq_test.gen_connack(rc=0)

subscribe_packet = mosq_test.gen_subscribe(mid, "subpub/qos2", 2)
suback_packet = mosq_test.gen_suback(mid, 2)

mid = 301
publish_packet = mosq_test.gen_publish("subpub/qos2", qos=2, mid=mid, payload="message")
pubrec_packet = mosq_test.gen_pubrec(mid)
pubrel_packet = mosq_test.gen_pubrel(mid)
pubcomp_packet = mosq_test.gen_pubcomp(mid)

mid = 1
publish_packet2 = mosq_test.gen_publish("subpub/qos2", qos=2, mid=mid, payload="message")
pubrec_packet2 = mosq_test.gen_pubrec(mid)
pubrel_packet2 = mosq_test.gen_pubrel(mid)
pubcomp_packet2 = mosq_test.gen_pubcomp(mid)

broker = subprocess.Popen(['../../src/mosquitto', '-p', '1888'], stderr=subprocess.PIPE)

try:
    time.sleep(0.5)

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(10)
    sock.connect(("localhost", 1888))
    sock.send(connect_packet)
    connack_recvd = sock.recv(256)

    if mosq_test.packet_matches("connack", connack_recvd, connack_packet):
        sock.send(subscribe_packet)
        suback_recvd = sock.recv(256)

        if mosq_test.packet_matches("suback", suback_recvd, suback_packet):
            sock.send(publish_packet)
            pubrec_recvd = sock.recv(256)

            if mosq_test.packet_matches("pubrec", pubrec_recvd, pubrec_packet):
                sock.send(pubrel_packet)
                pubcomp_recvd = sock.recv(256)

                if mosq_test.packet_matches("pubcomp", pubcomp_recvd, pubcomp_packet):
                    publish_recvd = sock.recv(256)

                    if mosq_test.packet_matches("publish2", publish_recvd, publish_packet2):
                        sock.send(pubrec_packet2)
                        pubrel_recvd = sock.recv(256)

                        if mosq_test.packet_matches("pubrel2", pubrel_recvd, pubrel_packet2):
                            # Broker side of flow complete so can quit here.
                            rc = 0

    sock.close()
finally:
    broker.terminate()
    broker.wait()

exit(rc)

