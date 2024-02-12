# -*- coding: utf-8 -*-
import serial
import os
from seplos_battery import SeplosBattery
from seplos_comm import Comm
from seplos_utils import logger


class SeplosPack(object):
    """
    """

    BATTERY_PACKS = 2
    BATTERY_PORTS = ['/dev/tty.usbserial-B0019Z73',
                     '/dev/tty.usbserial-B001AA8J',
                     '/dev/tty.usbserial-VE6NMUVK',
                     ]
    BATTERY_MASTER_BAUD = 9600
    BATTERY_SLAVE_BAUD = 19200
    POLL_INTERVAL = 5000

    def __init__(self) -> None:
        """
        """
        self.seplos_batteries = []
        self.setup_batteries()
        self.pos_master = -1
        self.pos_slave = -1

    def test_and_add_battery(self, serial_if: serial.Serial, address: int = 0):
        """
        """
        comm = Comm(serial_if, address)
        test_result = comm.test_connection()
        if test_result:
            self.seplos_batteries.append(SeplosBattery(comm))
            logger.debug(f"Connected to battery {address}")
        else:
            logger.debug(f"Failed to connect to battery {address}")
        return test_result

    def check_master(self):
        """
        """
        for index, port in enumerate(self.BATTERY_PORTS):
            if os.path.exists(port):
                logger.info(f"Test battery at {port}")
                serial_if = serial.Serial(port=port,
                                          baudrate=self.BATTERY_MASTER_BAUD,
                                          timeout=1)
                if self.test_and_add_battery(serial_if, address=0):
                    break
                serial_if.close()
        else:
            return -1
        return index

    def check_slave_port(self, port: str):
        """
        """
        logger.debug(f"Test battery at {port}")
        serial_if = serial.Serial(port=port,
                                  baudrate=self.BATTERY_SLAVE_BAUD,
                                  timeout=1)
        for i in range(1, self.BATTERY_PACKS):
            if self.test_and_add_battery(serial_if, address=i):
                break
        else:
            serial_if.close()
            return False
        return True

    def check_slaves(self):
        """
        """
        for index, port in enumerate(self.BATTERY_PORTS):
            if index == self.pos_master:
                logger.debug(f"Skip master battery at {index}")
                continue
            if os.path.exists(port):
                if self.check_slave_port(port=port):
                    break
        else:
            return -1
        return index

    def setup_batteries(self):
        """
        """
        self.pos_master = self.check_master()
        if self.pos_master == -1:
            logger.error(f"Master battery not found")
        else:
            logger.info(f"Master battery found at"
                        f" {self.BATTERY_PORTS[self.pos_master]}")

        self.pos_slave = self.check_slaves()
        if self.pos_slave == -1:
            logger.error(f"Slave battery not found")
        else:
            logger.info(f"Slave battery found at"
                        f" {self.BATTERY_PORTS[self.pos_master]}")
