#!/bin/bash

# remove comment for easier troubleshooting
#set -x

# backup old PageBattery.qml once. New firmware upgrade will remove the backup
if [ ! -f /opt/victronenergy/gui/qml/PageBattery.qml.backup ]; then
    cp /opt/victronenergy/gui/qml/PageBattery.qml /opt/victronenergy/gui/qml/PageBattery.qml.backup
fi
# backup old PageBatteryParameters.qml once. New firmware upgrade will remove the backup
if [ ! -f /opt/victronenergy/gui/qml/PageBatteryParameters.qml.backup ]; then
    cp /opt/victronenergy/gui/qml/PageBatteryParameters.qml /opt/victronenergy/gui/qml/PageBatteryParameters.qml.backup
fi
# backup old PageBatterySettings.qml once. New firmware upgrade will remove the backup
if [ ! -f /opt/victronenergy/gui/qml/PageBatterySettings.qml.backup ]; then
    cp /opt/victronenergy/gui/qml/PageBatterySettings.qml /opt/victronenergy/gui/qml/PageBatterySettings.qml.backup
fi
# backup old PageLynxIonIo.qml once. New firmware upgrade will remove the backup
if [ ! -f /opt/victronenergy/gui/qml/PageLynxIonIo.qml.backup ]; then
    cp /opt/victronenergy/gui/qml/PageLynxIonIo.qml /opt/victronenergy/gui/qml/PageLynxIonIo.qml.backup
fi
# copy new PageBattery.qml
cp /data/etc/dbus-seplos/qml/PageBattery.qml /opt/victronenergy/gui/qml/
# copy new PageBatteryCellVoltages
cp /data/etc/dbus-seplos/qml/PageBatteryCellVoltages.qml /opt/victronenergy/gui/qml/
# copy new PageBatteryParameters.qml
cp /data/etc/dbus-seplos/qml/PageBatteryParameters.qml /opt/victronenergy/gui/qml/
# copy new PageBatterySettings.qml
cp /data/etc/dbus-seplos/qml/PageBatterySettings.qml /opt/victronenergy/gui/qml/
# copy new PageBatterySetup
cp /data/etc/dbus-seplos/qml/PageBatterySetup.qml /opt/victronenergy/gui/qml/
# copy new PageLynxIonIo.qml
cp /data/etc/dbus-seplos/qml/PageLynxIonIo.qml /opt/victronenergy/gui/qml/



# stop gui
svc -d /service/gui
# sleep 1 sec
sleep 1
# start gui
svc -u /service/gui
