#!/bin/bash

export MALLOC_CHECK_=3
../../src/mosquitto -p 1888 &
PID=$!
echo ${PID} > broker.pid
sleep 1
