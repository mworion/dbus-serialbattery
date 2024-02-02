#!/bin/bash

# remove comment for easier troubleshooting
#set -x

# disable driver
bash /data/etc/dbus-serialseplos/scripts/disable.sh

# remove files in Victron directory. Don't use variables here,
# since on an error the whole /opt/victronenergy gets deleted
rm -rf /opt/victronenergy/service/dbus-serialseplos
rm -rf /opt/victronenergy/service-templates/dbus-serialseplos
rm -rf /opt/victronenergy/dbus-serialseplos

# restore GUI changes
/data/etc/dbus-serialseplos/scripts/restore-gui.sh

# uninstall modules
pip3 uninstall bleak
pip3 uninstall python-can
opkg remove python3-pip python3-modules
rm -rf /data/etc/dbus-serialseplos
