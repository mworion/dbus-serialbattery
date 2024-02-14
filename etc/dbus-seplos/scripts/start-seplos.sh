#!/bin/bash

# remove comment for easier troubleshooting
# set -x

. /opt/victronenergy/serial-starter/run-service.sh

app="python /data/etc/dbus-seplos/src/seplos_run.py"
args="/dev/$tty"
start $args
