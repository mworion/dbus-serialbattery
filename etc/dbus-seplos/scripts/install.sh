#!/bin/bash

# remove comment for easier troubleshooting
#set -x

## extract the tar file
if [ -f "/tmp/venus-data.tar.gz" ]; then
    rm -rf /data/etc/dbus-seplos
    tar -zxf /tmp/venus-data.tar.gz -C /data
else
    echo "There is no file in \"venus-data.tar.gz\""
    exit
fi

# install
rm -rf /opt/victronenergy/service-templates/dbus-seplos
cp -rf /data/etc/dbus-seplos/service /opt/victronenergy/service-templates/dbus-seplos
bash /data/etc/dbus-seplos/install-qml.sh

# kill driver, if running. It gets restarted by the service daemon
pkill -f "supervise dbus-seplos.*"
pkill -f "multilog .* /var/log/dbus-seplos.*"
pkill -f "python .*/dbus-seplos.py"