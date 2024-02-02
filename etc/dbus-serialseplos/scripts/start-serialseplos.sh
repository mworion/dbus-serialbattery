#!/bin/bash

# remove comment for easier troubleshooting
#set -x

. /opt/victronenergy/serial-starter/run-service.sh

# app=$(dirname $0)/src/dbus-serialseplos.py

# start -x -s $tty
app="python /opt/victronenergy/dbus-serialseplos/src/dbus-serialseplos.py"
args="/dev/$tty"
start $args
