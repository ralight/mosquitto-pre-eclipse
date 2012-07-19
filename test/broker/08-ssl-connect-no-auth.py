#!/usr/bin/python

# Test whether a valid CONNECT results in the correct CONNACK packet using an SSL connection.

import subprocess
import socket
import ssl
import time
from struct import *

if sys.version < '2.7':
    print("WARNING: SSL not supported on Python 2.6")
    exit(0)

rc = 1
keepalive = 10
connect_packet = pack('!BBH6sBBHH20s', 16, 12+2+20,6,"MQIsdp",3,2,keepalive,20,"connect-success-test")
connack_packet = pack('!BBBB', 32, 2, 0, 0);

broker = subprocess.Popen(['../../src/mosquitto', '-c', '08-ssl-connect-no-auth.conf'], stderr=subprocess.PIPE)

try:
    time.sleep(0.5)

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ssock = ssl.wrap_socket(sock, ca_certs="../ssl/test-ca.crt", cert_reqs=ssl.CERT_REQUIRED)
    ssock.settimeout(5)
    ssock.connect(("localhost", 1888))
    ssock.send(connect_packet)
    connack_recvd = ssock.recv(256)
    ssock.close()

    if connack_recvd != connack_packet:
        (cmd, rl, resv, ret) = unpack('!BBBB', connack_recvd)
        print("FAIL: Expected 32,2,0,0 got " + str(cmd) + "," + str(rl) + "," + str(resv) + "," + str(ret))
    else:
        rc = 0
finally:
    broker.terminate()
    broker.wait()

exit(rc)

