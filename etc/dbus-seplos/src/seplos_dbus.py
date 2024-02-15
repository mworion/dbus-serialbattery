# -*- coding: utf-8 -*-
import sys
import os
import platform
from time import time
from typing import Union
import dbus

sys.path.insert(1, os.path.join(os.path.dirname(__file__),
                                "/opt/victronenergy/dbus-systemcalc-py/ext/velib_python"))

from vedbus import VeDbusService
from settingsdevice import SettingsDevice
from seplos_utils import logger, DRIVER_VERSION, roundSec

# Victron packages


def get_bus() -> Union[dbus.SessionBus, dbus.SystemBus]:
    """
    """
    return (dbus.SessionBus() if "DBUS_SESSION_BUS_ADDRESS" in os.environ
            else dbus.SystemBus())


class DBUS:
    """
    """
    def __init__(self, pack):
        """
        """
        self.pack = pack
        self.number_batteries = len(pack.seplos_batteries)
        self.battery = [None] * self.number_batteries
        self.settings = [None] * self.number_batteries
        self.instance = [None] * self.number_batteries
        self.error = [None] * self.number_batteries
        self.dbusservice = [None] * self.number_batteries

        for i, battery in enumerate(pack.seplos_batteries):
            self.battery[i] = battery
            self.settings[i] = None
            self.error[i] = {"count": 0, "timestamp_first": None, "timestamp_last": None}
            self.dbusservice[i] = VeDbusService(
                f'com.victronenergy.battery.{battery.unique_identifier()}',
                get_bus())

    def get_role_instance(self, i:int) -> tuple:
        """
        """
        val = self.settings[i]["instance"].split(":")
        logger.info("DeviceInstance = %d", int(val[1]))
        return val[0], int(val[1])

    def handle_changed_setting(self, setting, old_value, new_value):
        """
        """
        if setting == "instance":
            _, instance = self.get_role_instance()
            logger.info(f'Changed Instance {instance}, '
                        f'old: {old_value}, new: {new_value}')

    def setup_instance(self, i:int) -> tuple:
        """
        """
        bms_id = self.battery[i].unique_identifier()
        path = "/Settings/Devices/seplos"
        default_instance = 'battery:1'
        settings = {"instance": [path + "_" + str(bms_id).replace(" ", "_") + "/ClassAndVrmInstance",
                                 default_instance, 0, 0, ]}

        self.settings[i] = SettingsDevice(get_bus(), settings,
                                          self.handle_changed_setting)
        self.battery[i].role, self.instance[i] = self.get_role_instance(i)
        return

    def setup_vedbus(self, i: int) -> bool:
        """
        """
        dbus = self.dbusservice[i]
        battery = self.battery[i]
        instance = self.instance[i]
        # Create the management objects, as specified in the ccgx dbus-api document
        dbus.add_path("/Mgmt/ProcessName", __file__)
        dbus.add_path("/Mgmt/ProcessVersion", "Python " + platform.python_version())
        dbus.add_path("/Mgmt/Connection", battery.connection_name())

        # Create the mandatory objects
        dbus.add_path("/DeviceInstance", instance)
        dbus.add_path("/ProductId", 0x0)
        dbus.add_path("/ProductName", battery.product_name())
        dbus.add_path("/FirmwareVersion", DRIVER_VERSION)
        dbus.add_path("/HardwareVersion", battery.hardware_version)
        dbus.add_path("/Connected", 1)
        dbus.add_path("/Seplos", battery.unique_identifier(), writeable=True)
        dbus.add_path("/DeviceName", battery.custom_name(), writeable=True)

        # Create static battery info
        dbus.add_path("/System/NrOfCellsPerBattery", battery.alarm.number_of_cells, writeable=True)
        dbus.add_path("/System/NrOfModulesOnline", 1, writeable=True)
        dbus.add_path("/System/NrOfModulesOffline", 0, writeable=True)
        dbus.add_path("/Capacity", battery.telemetry.battery_capacity,
                      writeable=True, gettextcallback=lambda p, v: "{:0.2f}Ah".format(v))
        dbus.add_path("/InstalledCapacity", battery.telemetry.rated_capacity,
                      writeable=True, gettextcallback=lambda p, v: "{:0.0f}Ah".format(v))
        dbus.add_path("/Soc", None, writeable=True)
        dbus.add_path("/Dc/0/Voltage", None, writeable=True,
                      gettextcallback=lambda p, v: "{:2.2f}V".format(v))
        dbus.add_path("/Dc/0/Current", None, writeable=True,
                      gettextcallback=lambda p, v: "{:2.2f}A".format(v))
        dbus.add_path("/Dc/0/Power", None, writeable=True,
                      gettextcallback=lambda p, v: "{:0.0f}W".format(v))
        dbus.add_path("/Dc/0/Temperature", None, writeable=True)

        # Create battery extras
        dbus.add_path("/System/MinCellTemperature", None, writeable=True)
        dbus.add_path("/System/MinTemperatureCellId", None, writeable=True)
        dbus.add_path("/System/MaxCellTemperature", None, writeable=True)
        dbus.add_path("/System/MaxTemperatureCellId", None, writeable=True)
        dbus.add_path("/System/MOSTemperature", None, writeable=True)
        dbus.add_path("/System/Temperature1", None, writeable=True)
        dbus.add_path("/System/Temperature1Name", None, writeable=True)
        dbus.add_path("/System/Temperature2", None, writeable=True)
        dbus.add_path("/System/Temperature2Name", None, writeable=True)
        dbus.add_path("/System/Temperature3", None, writeable=True)
        dbus.add_path("/System/Temperature3Name", None, writeable=True)
        dbus.add_path("/System/Temperature4", None, writeable=True)
        dbus.add_path("/System/Temperature4Name", None, writeable=True)
        dbus.add_path("/System/MaxCellVoltage", None, writeable=True,
                      gettextcallback=lambda p, v: "{:0.3f}V".format(v))
        dbus.add_path("/System/MaxVoltageCellId", None, writeable=True)
        dbus.add_path("/System/MinCellVoltage", None, writeable=True,
                      gettextcallback=lambda p, v: "{:0.3f}V".format(v))
        dbus.add_path("/System/MinVoltageCellId", None, writeable=True)
        dbus.add_path("/History/ChargeCycles", None, writeable=True)

        for i in range(1, battery.alarm.number_of_cells + 1):
            dbus.add_path(f'/Voltages/Cell{i:s}', None, writeable=True,
                          gettextcallback=lambda p, v: "{:0.3f}V".format(v))
            dbus.add_path(f'/Balances/Cell{i:s}', None, writeable=True)

        dbus.add_path("/Voltages/Sum", None, writeable=True,
                      gettextcallback=lambda p, v: "{:2.2f}V".format(v))
        dbus.add_path("/Voltages/Diff", None, writeable=True,
                      gettextcallback=lambda p, v: "{:0.3f}V".format(v))
        return True

    def setup_vedbus_pack(self) -> bool:
        """
        """
        for i in range(self.number_batteries):
            self.setup_instance(i)
            self.setup_vedbus(i)
        return True

    def publish_battery(self, loop, i:int):
        """
        This is called every battery.poll_interval millisecond as set up per
        battery type to read and update the data
        """
        try:
            result = self.battery[i].refresh_data()
            if result:
                self.error[i]["count"] = 0
                self.battery[i].online = True

            else:
                if self.error[i]["count"] == 0:
                    self.error[i]["timestamp_first"] = int(time())
                self.error[i]["timestamp_last"] = int(time())
                self.error[i]["count"] += 1
                time_since_first_error = (self.error[i]["timestamp_last"] - self.error[i]["timestamp_first"])
                if time_since_first_error >= 60:
                    loop.quit()

        except Exception:
            loop.quit()

    def publish_dbus(self, i:int):
        """
        """
        dbus = self.dbusservice[i]
        battery = self.battery[i]
        dbus["/System/NrOfCellsPerBattery"] = battery.alarm.number_of_cells
        dbus["/Soc"] = roundSec(battery.telemetry.soc, 2)
        dbus["/Dc/0/Voltage"] = roundSec(battery.telemetry.total_pack_voltage, 2)
        dbus["/Dc/0/Current"] = roundSec(battery.telemetry.dis_charge_current, 2)
        dbus["/Dc/0/Power"] = roundSec(battery.telemetry.dis_charge_power, 2)
        dbus["/Dc/0/Temperature"] = battery.telemetry.environ_temperature
        dbus["/Capacity"] = battery.telemetry.battery_capacity
        dbus["/History/ChargeCycles"] = battery.telemetry.cycles
        dbus["/System/NrOfModulesOnline"] = 1
        dbus["/System/NrOfModulesOffline"] = 0
        dbus["/System/MinCellTemperature"] = battery.telemetry.lowest_cell_temperature
        dbus["/System/MinTemperatureCellId"] = battery.telemetry.lowest_cell_tid
        dbus["/System/MaxCellTemperature"] = battery.telemetry.highest_cell_temperature
        dbus["/System/MaxTemperatureCellId"] = battery.telemetry.highest_cell_tid
        dbus["/System/MOSTemperature"] = battery.telemetry.power_temperature
        dbus["/System/Temperature1"] = battery.telemetry.temperature[0]
        dbus["/System/Temperature1Name"] = 'Temp 1'
        dbus["/System/Temperature2"] = battery.telemetry.temperature[1]
        dbus["/System/Temperature2Name"] = 'Temp 2'
        dbus["/System/Temperature3"] = battery.telemetry.temperature[2]
        dbus["/System/Temperature3Name"] = 'Temp 3'
        dbus["/System/Temperature4"] = battery.telemetry.temperature[3]
        dbus["/System/Temperature4Name"] = 'Temp 4'
        dbus["/System/MinVoltageCellId"] = battery.telemetry.lowest_cell_vid
        dbus["/System/MaxVoltageCellId"] = battery.telemetry.highest_cell_vid
        dbus["/System/MinCellVoltage"] = battery.telemetry.lowest_cell_voltage
        dbus["/System/MaxCellVoltage"] = battery.telemetry.highest_cell_voltage

        # cell voltages
        try:
            voltageSum = 0
            for i in range(battery.alarm.number_of_cells):
                voltage = battery.telemetry.cell_voltage[i]
                dbus[f'/Voltages/Cell{i:s}'] = voltage
                dbus[f'/Balances/Cell{i:s}'] = battery.alarm.cell_equalization[i]
                if voltage:
                    voltageSum += voltage
            dbus["/Voltages/Sum"] = voltageSum
            dbus["/Voltages/Diff"] = battery.telemetry.delta_cell_voltage

        except Exception:
            pass

    def publish_battery_pack(self, loop):
        """
        """
        for i in range(self.number_batteries):
            self.publish_battery(loop=loop, i=i)
            self.publish_dbus(i)
