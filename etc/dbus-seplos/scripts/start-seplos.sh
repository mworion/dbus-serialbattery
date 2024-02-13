#!/bin/bash

# remove comment for easier troubleshooting
set -x

. /opt/victronenergy/serial-starter/run-service.sh

app="python /data/etc/dbus-seplos/src/dbus-seplos.py"
args="/dev/$tty"
start $args