#!/usr/bin/python

import os
import subprocess
import socket
import sys
import time
from struct import *

import mosquitto


def on_connect(mosq, obj, rc):
    if rc != 0:
        exit(rc)

run = -1
mosq = mosquitto.Mosquitto("publish-qos1-test", run)
mosq.message_retry_set(3)
mosq.on_connect = on_connect

mosq.connect("localhost", 1888)
rc = 0
while run == -1 and rc == 0:
    rc = mosq.loop()

exit(run)
