# -*- coding: utf-8 -*-
import serial
from battery import Battery, Cell
from seplos_telecommand import Telecommand
from seplos_telemetry import Telemetry
from seplos_comm import Comm


class Seplos(Battery):
    BATTERYTYPE = "Seplos"
    BATTERY_PACKS = 2
    BATTERY_MASTER_PORT = '/dev/ttyUSB2'
    BATTERY_MASTER_BAUD = 9600
    BATTERY_SLAVE_PORT= '/dev/ttyUSB3'
    BATTERY_SLAVE_BAUD = 19200
    COMMAND_PROTOCOL_VERSION = 0x4F
    COMMAND_VENDOR_INFO = 0x51

    def __init__(self, port, baud, address=0x00):
        self.type = self.BATTERYTYPE
        self.address = address
        self.port = port
        self.baud = baud
        self.poll_interval = 5000
        self.telecommand = Telecommand()
        self.telemetry = Telemetry()
        self.comm = [None] * self.BATTERY_PACKS

        self.comm[0] = Comm(serial.Serial(port=self.BATTERY_MASTER_PORT,
                                          baudrate=self.BATTERY_MASTER_BAUD,
                                          timeout=1))
        for i in range(1, self.BATTERY_PACKS):
            self.comm[i] = Comm(serial.Serial(port=self.BATTERY_SLAVE_PORT,
                                              baudrate=self.BATTERY_SLAVE_BAUD,
                                              timeout=1))

    def refresh_data(self):
        """
        Call all functions that will refresh the battery data.
        This will be called for every iteration (self.poll_interval)
        Return True if success, False for failure
        """
        result_status = self.comm.read_status_data()
        self.telecommand.decode(result_status)
        result_alarm = self.comm.read_alarm_data()
        self.telemetry.decode(result_alarm)
        return result_status and result_alarm
