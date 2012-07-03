#!/usr/bin/python

# Test whether a client subscribed to a topic receives its own message sent to that topic.

import subprocess
import socket
import time
from struct import *

rc = 1
mid = 530
keepalive = 60
connect_packet = pack('!BBH6sBBHH16s', 16, 12+2+16,6,"MQIsdp",3,2,keepalive,16,"subpub-qos1-test")
connack_packet = pack('!BBBB', 32, 2, 0, 0);

subscribe_packet = pack('!BBHH11sB', 130, 2+2+11+1, mid, 11, "subpub/qos1", 1)
suback_packet = pack('!BBHB', 144, 2+1, mid, 1)

mid = 300
publish_packet = pack('!BBH11sH7s', 48+2, 2+11+2+7, 11, "subpub/qos1", mid, "message")
puback_packet = pack('!BBH', 64, 2, mid)

mid = 1
publish_packet2 = pack('!BBH11sH7s', 48+2, 2+11+2+7, 11, "subpub/qos1", mid, "message")

broker = subprocess.Popen(['../../src/mosquitto', '-p', '1888'], stderr=subprocess.PIPE)

try:
    time.sleep(0.5)

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(10)
    sock.connect(("localhost", 1888))
    sock.send(connect_packet)
    connack_recvd = sock.recv(256)

    if connack_recvd != connack_packet:
        print("FAIL: Connect failed.")
    else:
        sock.send(subscribe_packet)
        suback_recvd = sock.recv(256)

        if suback_recvd != suback_packet:
            (cmd, rl, mid_recvd, qos) = unpack('!BBHB', suback_recvd)
            print("FAIL: Expected 144,3,"+str(mid)+",0 got " + str(cmd) + "," + str(rl) + "," + str(mid_recvd) + "," + str(qos))
        else:
            sock.send(publish_packet)
            puback_recvd = sock.recv(256)

            if puback_recvd != puback_packet:
                (cmd, rl, mid_recvd) = unpack('!BBH', puback_recvd)
                print("FAIL: Expected 64,2,"+str(mid)+" got " + str(cmd) + "," + str(rl) + "," + str(mid_recvd))
            else:
                publish_recvd = sock.recv(256)

                if publish_recvd != publish_packet2:
                    print("FAIL: Received incorrect publish.")
                    print("Received: "+publish_recvd+" length="+str(len(publish_recvd)))
                    print("Expected: "+publish_packet2+" length="+str(len(publish_packet2)))
                else:
                    rc = 0

    sock.close()
finally:
    broker.terminate()
    broker.wait()

exit(rc)

