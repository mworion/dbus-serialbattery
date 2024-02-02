#!/bin/bash

# remove comment for easier troubleshooting
#set -x

# handle read only mounts
bash /opt/victronenergy/swupdate-scripts/remount-rw.sh

# remove driver from serial starter
rm -f /data/conf/serial-starter.d/dbus-serialseplos.conf
# remove serial-starter.d if empty
rmdir /data/conf/serial-starter.d >/dev/null 2>&1
# kill serial starter, to reload changes
pkill -f "/opt/victronenergy/serial-starter/serial-starter.sh"

# remove services
rm -rf /service/dbus-serialseplos.*
rm -rf /service/dbus-blebattery.*
rm -rf /service/dbus-canbattery.*

# kill driver, if running
# serial
pkill -f "supervise dbus-serialseplos.*"
pkill -f "multilog .* /var/log/dbus-serialseplos.*"
pkill -f "python .*/dbus-serialseplos.py /dev/tty.*"

# remove install script from rc.local
sed -i "/bash \/data\/etc\/dbus-serialseplos\/reinstall-local.sh/d" /data/rc.local

# remove cronjob
sed -i "/5 0,12 \* \* \* \/etc\/init.d\/bluetooth restart/d" /var/spool/cron/root >/dev/null 2>&1

echo "The dbus-serialseplos driver was disabled".
echo
