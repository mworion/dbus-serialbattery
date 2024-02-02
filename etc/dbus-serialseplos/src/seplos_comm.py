# -*- coding: utf-8 -*-
import serial
import time
from seplos_utils import logger
from seplos_protocol import is_valid_hex_string, is_valid_frame, is_valid_length
from seplos_protocol import encode_cmd


class Comm:
    COMMAND_STAT = 0x42
    COMMAND_STAT_LENGTH = 168
    COMMAND_ALARM = 0x44
    COMMAND_ALARM_LENGTH = 98

    def __init__(self, connection: serial.Serial):
        self.connection = connection

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
        self.connection.flushOutput()
        self.connection.flushInput()
        self.connection.write(command)
        time.sleep(0.1)
        data = self.connection.readline()

        if not is_valid_hex_string(data):
            return False
        if not is_valid_frame(data):
            return False
        if not is_valid_length(data, response_length):
            return False

        length_pos = 10
        return_data = data[length_pos + 3: -5]
        return return_data

    def read_alarm_data(self):
        """
        """
        command = encode_cmd(address=0x00, cid2=self.COMMAND_ALARM, info=b"01")
        data = self.read_serial_data(command, self.COMMAND_ALARM_LENGTH)
        if not data:
            return False
        return data

    def read_status_data(self):
        """
        """
        command = encode_cmd(address=0x00, cid2=self.COMMAND_STAT, info=b"01")
        data = self.read_serial_data(command, self.COMMAND_STAT_LENGTH)
        if not data:
            return False
        return data
