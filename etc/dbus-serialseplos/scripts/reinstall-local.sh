#!/bin/bash

# remove comment for easier troubleshooting
#set -x

# handle read only mounts
bash /opt/victronenergy/swupdate-scripts/remount-rw.sh

# install
rm -rf /opt/victronenergy/service/dbus-seplos
rm -rf /opt/victronenergy/service-templates/dbus-seplos
rm -rf /opt/victronenergy/dbus-seplos
mkdir /opt/victronenergy/dbus-seplos

cp -f /data/etc/dbus-seplos/* /opt/victronenergy/dbus-seplos &>/dev/null
cp -rf /data/etc/dbus-seplos/service /opt/victronenergy/service-templates/dbus-seplos
bash /data/etc/dbus-seplos/install-qml.sh



# add install-script to rc.local to be ready for firmware update
filename=/data/rc.local
if [ ! -f "$filename" ]; then
    echo "#!/bin/bash" > "$filename"
    chmod 755 "$filename"
fi
grep -qxF "bash /data/etc/dbus-seplos/scripts/reinstall-local.sh" $filename
 || echo "bash /data/etc/dbus-seplos/scripts/reinstall-local.sh" >> $filename


# kill driver, if running. It gets restarted by the service daemon
pkill -f "supervise dbus-seplos.*"
pkill -f "multilog .* /var/log/dbus-seplos.*"
pkill -f "python .*/dbus-seplos.py /dev/tty.*"
