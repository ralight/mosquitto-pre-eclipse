#!/usr/bin/env python

# Test whether a connection is successful with correct username and password
# when using a simple auth_plugin.

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
keepalive = 10
connect_packet = mosq_test.gen_connect("connect-uname-pwd-test", keepalive=keepalive, username="test-username", password="wrong")
connack_packet = mosq_test.gen_connack(rc=4)

broker = subprocess.Popen(['../../src/mosquitto', '-c', '09-plugin-auth-unpwd-fail.conf'], stderr=subprocess.PIPE)

try:
    time.sleep(0.5)

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(20)
    sock.connect(("localhost", 1888))
    sock.send(connect_packet)

    if mosq_test.expect_packet(sock, "connack", connack_packet):
        rc = 0

    sock.close()
finally:
    broker.terminate()
    broker.wait()
    if rc:
        (stdo, stde) = broker.communicate()
        print(stde)

exit(rc)

