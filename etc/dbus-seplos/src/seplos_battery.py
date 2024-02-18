# -*- coding: utf-8 -*-
from seplos_alarm import Alarm
from seplos_telemetry import Telemetry
from seplos_comm import Comm
from seplos_protocol import encode_cmd
from seplos_utils import logger


class SeplosBattery:
    """
    """
    PRODUCT = "Seplos BMS"
    PRODUCT_ID = "001"
    HARDWARE_VERSION = "none"

    CID1 = 0x46                 # Lithium iron phosphate battery BMS
    TELEMETRY = 0x42            # Acquisition of telemetering information
    TELEMETRY_LENGTH = 150
    ALARM = 0x44                # Acquisition of telecommand information
    ALARM_LENGTH = 98
    PROTOCOL = 0x4F             # Protocol version
    PROTOCOL_LENGTH = 0
    VENDOR = 0x4F               # Vendor Data
    VENDOR_LENGTH = 30

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
        return f'Seplos {self.comm.address}'

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

    def read_protocol_data(self):
        """
        ~  2  0  0  0  4  6  4  F  0  0  0  0  F  D  9  A  $
        ~  2  0  0  0  4  6  0  0  0  0  0  0  F  D  B  4  $
        """
        info = f'{self.comm.address:02X}'.encode()
        command = encode_cmd(address=self.comm.address, cid1=self.CID1,
                             cid2=self.PROTOCOL, info=info)
        ok, data = self.comm.read_serial_data(command, self.PROTOCOL_LENGTH)
        if not ok:
            logger.error(f"Failed to read protocol data from {self.comm.address}")
        return ok, data

    def read_vendor_data(self):
        """
        ~  2  0  0  0  4  6  5  1  0  0  0  0  F  D  A  E  $
        ~  2  0  0  0  4  6  0  0  C  0  4  0  3  1  3  1  3  0  3  1  2  D  4  C  4  E  3  1  3  2  2  0  1  0  0  6  4  3  4  1  4  E  3  A  5  6  6  9  6  3  7  4  7  2  6  F  6  E  2  0  2  0  2  0  2  0  2  0  2  0  2  0  2  0  2  0  F  0  7  D  $
        ~  2  0  0  0  4  6  0  0  C  0  4  0  3  1  3  1  3  0  3  1  2  D  4  C  4  E  3  1  3  2  2  0  1  0  0  6  4  3  4  1  4  E  3  A  5  6  6  9  6  3  7  4  7  2  6  F  6  E  2  0  2  0  2  0  2  0  2  0  2  0  2  0  2  0  2  0  F  0  7  D  $
        """
        info = f'{self.comm.address:02X}'.encode()
        command = encode_cmd(address=self.comm.address, cid1=self.CID1,
                             cid2=self.VENDOR, info=info)
        ok, data = self.comm.read_serial_data(command, self.VENDOR_LENGTH)
        if not ok:
            logger.error(f"Failed to read vendor data from {self.comm.address}")
        return ok, data

    def read_telemetry_data(self):
        """
        """
        info = f'{self.comm.address:02X}'.encode()
        command = encode_cmd(address=self.comm.address, cid1=self.CID1,
                             cid2=self.TELEMETRY, info=info)
        ok, data = self.comm.read_serial_data(command, self.TELEMETRY_LENGTH)
        if not ok:
            logger.error(f"Failed to read telemetry data from {self.comm.address}")
        return ok, data

    def get_telemetry(self) -> bool:
        """
        """
        ok, result_telemetry = self.read_telemetry_data()
        if ok:
            self.telemetry.decode_data(result_telemetry)
        return ok

    def read_alarm_data(self):
        """
        """
        info = f'{self.comm.address:02X}'.encode()
        command = encode_cmd(address=self.comm.address, cid1=self.CID1,
                             cid2=self.ALARM, info=info)
        ok, data = self.comm.read_serial_data(command, self.ALARM_LENGTH)
        if not ok:
            logger.error(f"Failed to read alarm data from {self.comm.address}")
        return ok, data

    def get_alarm(self) -> bool:
        """
        """
        ok, result_alarm = self.read_alarm_data()
        if ok:
            self.alarm.decode_data(result_alarm)
        return ok

    def get_all(self) -> bool:
        """
        """
        got_telemetry = self.get_telemetry()
        got_alarm = self.get_alarm()
        return got_telemetry and got_alarm
