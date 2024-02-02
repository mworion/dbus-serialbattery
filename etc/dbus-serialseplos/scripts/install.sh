#!/bin/bash

# remove comment for easier troubleshooting
#set -x


## extract the tar file
# extract driver
if [ -f "/tmp/venus-data.tar.gz" ]; then
    # remove old driver
    rm -rf /data/etc/dbus-serialseplos
    tar -zxf /tmp/venus-data.tar.gz -C /data
else
    echo "There is no file in \"venus-data.tar.gz\""
    exit
fi


# run install script >= v1.0.0
bash /data/etc/dbus-serialseplos/scripts/reinstall-local.sh
