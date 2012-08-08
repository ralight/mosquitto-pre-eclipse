#!/usr/bin/python

# Does a bridge resend a QoS=1 message correctly after a disconnect?

import os
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
client_id = socket.gethostname()+".bridge_sample"
connect_packet = mosq_test.gen_connect(client_id, keepalive=keepalive, clean_session=False, proto_ver=128+3)
connack_packet = mosq_test.gen_connack(rc=0)

mid = 1
subscribe_packet = mosq_test.gen_subscribe(mid, "bridge/#", 2)
suback_packet = mosq_test.gen_suback(mid, 2)

mid = 2
subscribe2_packet = mosq_test.gen_subscribe(mid, "bridge/#", 2)
suback2_packet = mosq_test.gen_suback(mid, 2)

mid = 3
subscribe3_packet = mosq_test.gen_subscribe(mid, "bridge/#", 2)
suback3_packet = mosq_test.gen_suback(mid, 2)

mid = 5
publish_packet = mosq_test.gen_publish("bridge/disconnect/test", qos=2, mid=mid, payload="disconnect-message")
publish_dup_packet = mosq_test.gen_publish("bridge/disconnect/test", qos=2, mid=mid, payload="disconnect-message", dup=True)
pubrec_packet = mosq_test.gen_pubrec(mid)
pubrel_packet = mosq_test.gen_pubrel(mid)
pubcomp_packet = mosq_test.gen_pubcomp(mid)

ssock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ssock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
ssock.settimeout(40)
ssock.bind(('', 1888))
ssock.listen(5)

broker = subprocess.Popen(['../../src/mosquitto', '-c', '06-bridge-b2br-disconnect-qos2.conf'], stderr=subprocess.PIPE)

try:
    time.sleep(0.5)

    (bridge, address) = ssock.accept()
    bridge.settimeout(10)
    connect_recvd = bridge.recv(len(connect_packet))

    if mosq_test.packet_matches("connect", connect_recvd, connect_packet):
        bridge.send(connack_packet)
        subscribe_recvd = bridge.recv(len(subscribe_packet))
        if mosq_test.packet_matches("subscribe", subscribe_recvd, subscribe_packet):
            bridge.send(suback_packet)

            bridge.send(publish_packet)
            bridge.close()

            (bridge, address) = ssock.accept()
            bridge.settimeout(10)
            connect_recvd = bridge.recv(len(connect_packet))

            if mosq_test.packet_matches("connect", connect_recvd, connect_packet):
                bridge.send(connack_packet)
                subscribe_recvd = bridge.recv(len(subscribe2_packet))
                if mosq_test.packet_matches("2nd subscribe", subscribe_recvd, subscribe2_packet):
                    bridge.send(suback2_packet)

                    bridge.send(publish_dup_packet)
                    pubrec_recvd = bridge.recv(len(pubrec_packet))
                    if mosq_test.packet_matches("pubrec", pubrec_recvd, pubrec_packet):
                        bridge.send(pubrel_packet)
                        bridge.close()

                        (bridge, address) = ssock.accept()
                        bridge.settimeout(10)
                        connect_recvd = bridge.recv(len(connect_packet))

                        if mosq_test.packet_matches("connect", connect_recvd, connect_packet):
                            bridge.send(connack_packet)
                            subscribe_recvd = bridge.recv(len(subscribe3_packet))
                            if mosq_test.packet_matches("3rd subscribe", subscribe_recvd, subscribe3_packet):
                                bridge.send(suback3_packet)

                                bridge.send(publish_dup_packet)
                                pubrec_recvd = bridge.recv(len(pubrec_packet))
                                if mosq_test.packet_matches("2nd pubrec", pubrec_recvd, pubrec_packet):
                                    bridge.send(pubrel_packet)
                                    pubcomp_recvd = bridge.recv(len(pubcomp_packet))

                                    if mosq_test.packet_matches("pubcomp", pubcomp_recvd, pubcomp_packet):
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

