#!/bin/bash

# remove comment for easier troubleshooting
#set -x

# handle read only mounts
bash /opt/victronenergy/swupdate-scripts/remount-rw.sh

# install
rm -rf /opt/victronenergy/service/dbus-serialseplos
rm -rf /opt/victronenergy/service-templates/dbus-serialseplos
rm -rf /opt/victronenergy/dbus-serialseplos
mkdir /opt/victronenergy/dbus-serialseplos
cp -f /data/etc/dbus-serialseplos/* /opt/victronenergy/dbus-serialseplos &>/dev/null
cp -rf /data/etc/dbus-serialseplos/service /opt/victronenergy/service-templates/dbus-serialseplos
bash /data/etc/dbus-serialseplos/install-qml.sh

# check if serial-starter.d was deleted
serialstarter_path="/data/conf/serial-starter.d"
serialstarter_file="$serialstarter_path/dbus-serialseplos.conf"

# check if folder is a file (older versions of this driver < v1.0.0)
if [ -f "$serialstarter_path" ]; then
    rm -f "$serialstarter_path"
fi

# check if folder exists
if [ ! -d "$serialstarter_path" ]; then
    mkdir "$serialstarter_path"
fi

# check if file exists
if [ ! -f "$serialstarter_file" ]; then
    {
        echo "service sbattery        dbus-serialseplos"
        echo "alias default gps:vedirect:sbattery"
        echo "alias rs485 cgwacs:fzsonick:imt:modbus:sbattery"
    } > "$serialstarter_file"
fi

# add install-script to rc.local to be ready for firmware update
filename=/data/rc.local
if [ ! -f "$filename" ]; then
    echo "#!/bin/bash" > "$filename"
    chmod 755 "$filename"
fi
grep -qxF "bash /data/etc/dbus-serialseplos/scripts/reinstall-local.sh" $filename
 || echo "bash /data/etc/dbus-serialseplos/scripts/reinstall-local.sh" >> $filename


# kill driver, if running. It gets restarted by the service daemon
pkill -f "supervise dbus-serialseplos.*"
pkill -f "multilog .* /var/log/dbus-serialseplos.*"
pkill -f "python .*/dbus-serialseplos.py /dev/tty.*"
