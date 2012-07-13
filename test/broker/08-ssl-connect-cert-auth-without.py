#!/usr/bin/python

# Test whether a client can connect without an SSL certificate if one is required.
# 

import subprocess
import socket
import ssl
import time
from struct import *

rc = 1
keepalive = 10
connect_packet = pack('!BBH6sBBHH17s', 16, 12+2+17,6,"MQIsdp",3,2,keepalive,17,"connect-cert-test")
connack_packet = pack('!BBBB', 32, 2, 0, 0);

broker = subprocess.Popen(['../../src/mosquitto', '-c', '08-ssl-connect-cert-auth-without.conf'], stderr=subprocess.PIPE)

time.sleep(0.5)

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ssock = ssl.wrap_socket(sock, ca_certs="../ssl/test-ca.crt", cert_reqs=ssl.CERT_REQUIRED)
ssock.settimeout(5)
try:
    ssock.connect(("localhost", 1888))
except ssl.SSLError as err:
    if err.errno == 1:
        rc = 0

broker.terminate()
broker.wait()

exit(rc)

