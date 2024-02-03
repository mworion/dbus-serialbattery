# -*- coding: utf-8 -*-
import serial
import time
from seplos_utils import logger
from seplos_protocol import is_valid_hex_string, is_valid_frame, is_valid_length
from seplos_protocol import encode_cmd


class Comm:
    TELEMETRY = 0x42
    TELEMETRY_LENGTH = 150
    ALARM = 0x44
    ALARM_LENGTH = 98
    NUMBER_OF_RETRIES = 5

    def __init__(self, connection: serial.Serial, address: int = 0):
        self.connection = connection
        self.address = address

    def test_connection(self):
        """
        call a function that will connect to the battery, send a command
        and retrieve the result. The result or call should be unique to this
        BMS. Battery name or version, etc.
        Return True if success, False for failure
        """
        try:
            result = self.read_status_data()
        except Exception as err:
            logger.error(f"Unexpected {err=}, {type(err)=}")
            result = False

        return result

    def read_serial_data(self, command, response_length=0):
        """
        """
        retries = self.NUMBER_OF_RETRIES
        self.connection.flushOutput()
        self.connection.flushInput()

        while retries > 0:
            self.connection.write(command)
            time.sleep(0.1)
            data_raw = self.connection.read_until(b'\r')
            data = data_raw[13: -5]

            if ((is_valid_length(data, response_length) and
                    is_valid_hex_string(data)) and
                    is_valid_frame(data=data_raw)):
                break
            retries -= 1

        if retries != 0:
            return data
        else:
            return False

    def read_alarm_data(self):
        """
        """
        info = f'{self.address:02X}'.encode()
        command = encode_cmd(address=self.address, cid2=self.ALARM, info=info)
        data = self.read_serial_data(command, self.ALARM_LENGTH)
        if not data:
            return False
        return data

    def read_telemetry_data(self):
        """
        """
        info = f'{self.address:02X}'.encode()
        command = encode_cmd(address=self.address, cid2=self.TELEMETRY, info=info)
        data = self.read_serial_data(command, self.TELEMETRY_LENGTH)
        if not data:
            return False
        return data
