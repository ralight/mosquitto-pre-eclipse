#!/bin/bash

../../src/mosquitto -p 1888 &
PID=$!
echo ${PID} > broker.pid
sleep 1
