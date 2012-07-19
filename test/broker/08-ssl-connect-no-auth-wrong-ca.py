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

broker = subprocess.Popen(['../../src/mosquitto', '-c', '08-ssl-connect-no-auth-wrong-ca.conf'], stderr=subprocess.PIPE)

time.sleep(0.5)

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ssock = ssl.wrap_socket(sock, ca_certs="../ssl/test-ca-alt.crt", cert_reqs=ssl.CERT_REQUIRED)
ssock.settimeout(5)
try:
    ssock.connect(("localhost", 1888))
except ssl.SSLError as err:
    if err.errno == 1:
        rc = 0

broker.terminate()
broker.wait
exit(rc)

