# -*- coding: utf-8 -*-
from seplos_alarm import Alarm
from seplos_telemetry import Telemetry
from seplos_comm import Comm
from seplos_protocol import encode_cmd
from seplos_utils import logger


class SeplosBattery(object):
    """
    """
    BATTERY_TYPE = "Seplos"

    CID1 = 0x46                 # Lithium iron phosphate battery BMS
    TELEMETRY = 0x42            # Acquisition of telemetering information
    TELEMETRY_LENGTH = 150
    ALARM = 0x44                # Acquisition of telecommand information
    ALARM_LENGTH = 98

    def __init__(self, comm: Comm) -> None:
        """
        """
        self.type = self.BATTERY_TYPE + f" {comm.address}"
        self.comm = comm
        self.alarm = Alarm()
        self.telemetry = Telemetry()

    def read_telemetry_data(self):
        """
        """
        info = f'{self.comm.address:02X}'.encode()
        command = encode_cmd(address=self.comm.address, cid1=self.CID1,
                             cid2=self.TELEMETRY, info=info)
        data = self.comm.read_serial_data(command, self.TELEMETRY_LENGTH)
        if not data:
            logger.error(f"Failed to read telemetry data from {self.comm.address}")
            return False
        return data

    def read_alarm_data(self):
        """
        """
        info = f'{self.comm.address:02X}'.encode()
        command = encode_cmd(address=self.comm.address, cid1=self.CID1,
                             cid2=self.ALARM, info=info)
        data = self.comm.read_serial_data(command, self.ALARM_LENGTH)
        if not data:
            logger.error(f"Failed to read alarm data from {self.comm.address}")
            return False
        return data

    def refresh_data(self):
        """
        """
        result_alarm = self.read_alarm_data()
        if not result_alarm:
            return False
        self.alarm.decode_data(result_alarm)

        result_telemetry = self.read_telemetry_data()
        if not result_telemetry:
            return False
        self.telemetry.decode_data(result_telemetry)

        return True
