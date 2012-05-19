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
    else:
        mosq.subscribe("qos1/test", 1)

def on_disconnect(mosq, obj, rc):
    obj = rc


run = -1
mosq = mosquitto.Mosquitto("subscribe-qos1-test", run)
mosq.on_connect = on_connect
mosq.on_disconnect = on_disconnect

mosq.connect("localhost", 1888)
while run == -1:
    mosq.loop()

exit(run)
