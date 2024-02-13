# -*- coding: utf-8 -*-
import serial
import time
from seplos_utils import logger
from seplos_protocol import is_valid_hex_string, is_valid_frame, is_valid_length
from seplos_protocol import encode_cmd


class Comm:
    """
    """
    NUMBER_OF_RETRIES = 5

    def __init__(self, serial_if: serial.Serial, address: int = 0):
        self.serial_if = serial_if
        self.address = address

    def test_connection(self):
        """
        Calling cid2=0x00 is invalid. We wait if the result is OK.
        """
        try:
            command = encode_cmd(address=self.address, cid1=0x46, cid2=0x00)
            response = self.read_serial_data(command, 0)
        except serial.SerialTimeoutException:
            logger.debug(f"Timeout from {self.address}")
            return False
        except Exception as err:
            logger.debug(f"Unexpected {err=}")
            return False
        return response == b''

    def read_serial_data(self, command, response_length=0):
        """
        """
        retries = self.NUMBER_OF_RETRIES
        # self.serial_if.close()
        # time.sleep(0.2)
        # self.serial_if.open()
        # time.sleep(0.2)

        data = None
        while retries > 0:
            self.serial_if.flushOutput()
            self.serial_if.flushInput()
            time.sleep(0.1)
            self.serial_if.write(command)
            try:
                data_raw = self.serial_if.read_until(b'\r')
                data = data_raw[13: -5]
            except serial.serialutil.SerialException:
                logger.debug(f"Serial exception from {self.address}")
                data = b''
                data_raw = b''

            if ((is_valid_length(data, response_length) and
                    is_valid_hex_string(data)) and
                    is_valid_frame(data=data_raw)):
                break
            retries -= 1

        if retries != 0:
            return data
        else:
            logger.debug(f"Exceeded retries from {self.address}")
            return False
