# -*- coding: utf-8 -*-
import serial
from seplos_alarm import Alarm
from seplos_telemetry import Telemetry
from seplos_comm import Comm


class SeplosBattery():
    BATTERYTYPE = "Seplos"
    BATTERY_PACKS = 2
    BATTERY_MASTER_PORT = '/dev/tty.usbserial-B0019Z73'
    BATTERY_MASTER_BAUD = 9600
    BATTERY_SLAVE_PORT = '/dev/tty.usbserial-B001AA8J'
    BATTERY_SLAVE_BAUD = 19200
    COMMAND_PROTOCOL_VERSION = 0x4F
    COMMAND_VENDOR_INFO = 0x51

    def __init__(self) -> None:
        self.type = self.BATTERYTYPE
        self.poll_interval = 5000
        self.alarm = Alarm()
        self.telemetry = Telemetry()
        self.comm = [None] * self.BATTERY_PACKS

        self.comm[0] = Comm(serial.Serial(port=self.BATTERY_MASTER_PORT,
                                          baudrate=self.BATTERY_MASTER_BAUD,
                                          timeout=1))
        if self.BATTERY_PACKS > 1:
            serial_if = serial.Serial(port=self.BATTERY_SLAVE_PORT,
                                      baudrate=self.BATTERY_SLAVE_BAUD,
                                      timeout=1)
        for i in range(1, self.BATTERY_PACKS):
            self.comm[i] = Comm(serial_if, address=i)

    def refresh_data(self):
        """
        Call all functions that will refresh the battery data.
        This will be called for every iteration (self.poll_interval)
        Return True if success, False for failure
        """
        result_alarm = self.comm.read_alarm_data()
        self.alarm.decode(result_alarm)
        result_telemetry = self.comm.read_telemetry_data()
        self.telemetry.decode(result_telemetry)
        return result_alarm and result_telemetry
