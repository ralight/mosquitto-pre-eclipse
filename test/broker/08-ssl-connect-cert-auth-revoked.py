#!/usr/bin/python

# Test whether a valid CONNECT results in the correct CONNACK packet using an
# SSL connection with client certificates required.

import subprocess
import socket
import ssl
import sys
import time
from struct import *

if sys.version < '2.7':
    print("WARNING: SSL not supported on Python 2.6")
    exit(0)

import inspect, os, sys
# From http://stackoverflow.com/questions/279237/python-import-a-module-from-a-folder
cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],"..")))
if cmd_subfolder not in sys.path:
    sys.path.insert(0, cmd_subfolder)

import mosq_test

rc = 1
keepalive = 10
connect_packet = pack('!BBH6sBBHH20s', 16, 12+2+20,6,"MQIsdp",3,2,keepalive,20,"connect-revoked-test")
connack_packet = pack('!BBBB', 32, 2, 0, 0);

broker = subprocess.Popen(['../../src/mosquitto', '-c', '08-ssl-connect-cert-auth-revoked.conf'], stderr=subprocess.PIPE)

try:
    time.sleep(0.5)

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ssock = ssl.wrap_socket(sock, ca_certs="../ssl/test-ca.crt", certfile="../ssl/client.crt", keyfile="../ssl/client.key", cert_reqs=ssl.CERT_REQUIRED)
    ssock.settimeout(5)
    try:
        ssock.connect(("localhost", 1888))
    except ssl.SSLError as err:
        if err.errno == 1:
            rc = 0
        else:
            broker.terminate()
            raise ValueError(err.errno)

finally:
    broker.terminate()
    broker.wait()

exit(rc)

