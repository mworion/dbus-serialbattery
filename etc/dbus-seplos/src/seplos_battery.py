# -*- coding: utf-8 -*-
from seplos_alarm import Alarm
from seplos_telemetry import Telemetry
from seplos_comm import Comm
from seplos_protocol import encode_cmd
from seplos_utils import logger


class SeplosBattery:
    """
    """
    PRODUCT = "EEL Battery"
    PRODUCT_ID = "001"
    HARDWARE_VERSION = "none"

    CID1 = 0x46                 # Lithium iron phosphate battery BMS
    TELEMETRY = 0x42            # Acquisition of telemetering information
    TELEMETRY_LENGTH = 150
    ALARM = 0x44                # Acquisition of telecommand information
    ALARM_LENGTH = 98

    def __init__(self, comm: Comm, port: str) -> None:
        """
        """
        self.port = port
        self.role = "battery"
        self.comm = comm
        self.online = True
        self.max_battery_charge_current = 200
        self.max_battery_discharge_current = 200
        self.alarm = Alarm()
        self.telemetry = Telemetry()

    def connection_name(self) -> str:
        """
        """
        return self.port[self.port.rfind("/") + 1:]

    def custom_name(self) -> str:
        """
        """
        return f'Seplos {self.comm.address})'

    def unique_identifier(self) -> str:
        """
        """
        return self.port[self.port.rfind("/") + 1:]

    def product_name(self) -> str:
        """
        """
        if self.comm.address == 0:
            return f'{self.PRODUCT} Master'
        else:
            return f'{self.PRODUCT} Slave {self.comm.address}'

    def product_id(self) -> str:
        """
        """
        return f'{self.PRODUCT_ID}'

    def hardware_version(self) -> str:
        """
        """
        return f'{self.HARDWARE_VERSION}'

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
        if result_alarm:
            self.alarm.decode_data(result_alarm)

        result_telemetry = self.read_telemetry_data()
        if result_telemetry:
            self.telemetry.decode_data(result_telemetry)

        return True
