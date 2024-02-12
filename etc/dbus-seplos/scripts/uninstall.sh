#!/bin/bash

# remove comment for easier troubleshooting
#set -x

# disable driver
bash /data/etc/dbus-seplos/scripts/disable.sh

rm -rf /opt/victronenergy/service-templates/dbus-seplos

# restore GUI changes
/data/etc/dbus-serialseplos/scripts/restore-gui.sh

# uninstall modules
pip3 uninstall bleak
pip3 uninstall python-can
opkg remove python3-pip python3-modules
rm -rf /data/etc/dbus-seplos
