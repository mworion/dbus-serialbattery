# -*- coding: utf-8 -*-
from battery import Protection, Battery, Cell
from utils import logger
import utils
import serial
from seplos_protocol import SeplosProtocol


class Seplos(Battery):
    BATTERYTYPE = "Seplos"

    COMMAND_PROTOCOL_VERSION = 0x4F
    COMMAND_VENDOR_INFO = 0x51
    def __init__(self, port, baud, address=0x00):
        super(Seplos, self).__init__(port, baud, address)
        self.type = self.BATTERYTYPE
        self.poll_interval = 5000

    def get_settings(self):
        # After successful connection get_settings will be called to set up the battery.
        # Set the current limits, populate cell count, etc.
        # Return True if success, False for failure

        # BMS does not provide max charge-/discharge, so we have to use hardcoded/config values
        self.max_battery_charge_current = utils.MAX_BATTERY_CHARGE_CURRENT
        self.max_battery_discharge_current = utils.MAX_BATTERY_DISCHARGE_CURRENT

        self.max_battery_voltage = utils.MAX_CELL_VOLTAGE * self.cell_count
        self.min_battery_voltage = utils.MIN_CELL_VOLTAGE * self.cell_count

        # init the cell array
        for _ in range(self.cell_count):
            self.cells.append(Cell(False))

        return True

    def refresh_data(self):
        # call all functions that will refresh the battery data.
        # This will be called for every iteration (self.poll_interval)
        # Return True if success, False for failure
        result_status = self.read_status_data()
        result_alarm = self.read_alarm_data()

        return result_status and result_alarm

    @staticmethod
    def decode_alarm_byte(data_byte: int, alarm_bit: int, warn_bit: int):
        if data_byte & (1 << alarm_bit) != 0:
            return Protection.ALARM
        if data_byte & (1 << warn_bit) != 0:
            return Protection.WARNING
        return Protection.OK

    def decode_alarm_data(self, data: bytes):
        logger.debug("alarm info decoded {}".format(data))
        voltage_alarm_byte = data[30]
        self.protection.voltage_cell_low = Seplos.decode_alarm_byte(
            data_byte=voltage_alarm_byte, alarm_bit=3, warn_bit=2
        )
        # cell high voltage is actually unused because DBUS does not seem to support it, decoding anyway
        # c.f. https://github.com/victronenergy/venus/wiki/dbus#battery
        self.protection.voltage_cell_high = Seplos.decode_alarm_byte(
            data_byte=voltage_alarm_byte, alarm_bit=1, warn_bit=0
        )
        self.protection.voltage_low = Seplos.decode_alarm_byte(
            data_byte=voltage_alarm_byte, alarm_bit=7, warn_bit=6
        )
        self.protection.voltage_high = Seplos.decode_alarm_byte(
            data_byte=voltage_alarm_byte, alarm_bit=5, warn_bit=4
        )

        temperature_alarm_byte = data[31]
        self.protection.temp_low_charge = Seplos.decode_alarm_byte(
            data_byte=temperature_alarm_byte, alarm_bit=3, warn_bit=2
        )
        self.protection.temp_high_charge = Seplos.decode_alarm_byte(
            data_byte=temperature_alarm_byte, alarm_bit=1, warn_bit=0
        )
        self.protection.temp_low_discharge = Seplos.decode_alarm_byte(
            data_byte=temperature_alarm_byte, alarm_bit=7, warn_bit=6
        )
        self.protection.temp_high_discharge = Seplos.decode_alarm_byte(
            data_byte=temperature_alarm_byte, alarm_bit=5, warn_bit=4
        )

        current_alarm_byte = data[33]
        self.protection.current_over = Seplos.decode_alarm_byte(
            data_byte=current_alarm_byte, alarm_bit=1, warn_bit=0
        )
        self.protection.current_under = Seplos.decode_alarm_byte(
            data_byte=current_alarm_byte, alarm_bit=3, warn_bit=2
        )

        soc_alarm_byte = data[34]
        self.protection.soc_low = Seplos.decode_alarm_byte(
            data_byte=soc_alarm_byte, alarm_bit=3, warn_bit=2
        )

        switch_byte = data[35]
        self.discharge_fet = True if switch_byte & 0b01 != 0 else False
        self.charge_fet = True if switch_byte & 0b10 != 0 else False
        return True

    def decode_status_data(self, data):
        cell_count_offset = 4
        voltage_offset = 6
        temps_offset = 72
        self.cell_count = Seplos.int_from_1byte_hex_ascii(
            data=data, offset=cell_count_offset
        )
        if self.cell_count == len(self.cells):
            for i in range(self.cell_count):
                voltage = (
                    Seplos.int_from_2byte_hex_ascii(data, voltage_offset + i * 4) / 1000
                )
                self.cells[i].voltage = voltage
                logger.debug("Voltage cell[{}]={}V".format(i, voltage))
            for i in range(min(4, self.cell_count)):
                temp = (
                    Seplos.int_from_2byte_hex_ascii(data, temps_offset + i * 4) - 2731
                ) / 10
                self.cells[i].temp = temp
                logger.debug("Temp cell[{}]={}°C".format(i, temp))
        self.temp1 = (
            Seplos.int_from_2byte_hex_ascii(data, temps_offset + 4 * 4) - 2731
        ) / 10
        self.temp2 = (
            Seplos.int_from_2byte_hex_ascii(data, temps_offset + 5 * 4) - 2731
        ) / 10
        self.current = (
            Seplos.int_from_2byte_hex_ascii(data, offset=96, signed=True) / 100
        )
        self.voltage = Seplos.int_from_2byte_hex_ascii(data, offset=100) / 100
        self.capacity_remain = Seplos.int_from_2byte_hex_ascii(data, offset=104) / 100
        self.capacity = Seplos.int_from_2byte_hex_ascii(data, offset=110) / 100
        self.soc = Seplos.int_from_2byte_hex_ascii(data, offset=114) / 10
        self.cycles = Seplos.int_from_2byte_hex_ascii(data, offset=122)
        self.hardware_version = "Seplos BMS {} cells".format(self.cell_count)
        logger.debug("Current = {}A , Voltage = {}V".format(self.current, self.voltage))
        logger.debug(
            "Capacity = {}/{}Ah , SOC = {}%".format(
                self.capacity_remain, self.capacity, self.soc
            )
        )
        logger.debug("Cycles = {}".format(self.cycles))
        logger.debug(
            "Environment temp = {}°C ,  Power temp = {}°C".format(
                self.temp1, self.temp2
            )
        )
        logger.debug("HW:" + self.hardware_version)

        return True

    @staticmethod
    def is_valid_frame(data: bytes) -> bool:
        """checks if data contains a valid frame
        * minimum length is 18 Byte
        * checksum needs to be valid
        * also checks for error code as return code in cid2
        * not checked: lchksum
        """
        if len(data) < 18:
            logger.debug("short read, data={}".format(data))
            return False

        chksum = Seplos.get_checksum(data[1:-5])
        if chksum != Seplos.int_from_2byte_hex_ascii(data, -5):
            logger.warning("checksum error")
            return False

        cid2 = data[7:9]
        if cid2 != b"00":
            logger.warning("command returned with error code {}".format(cid2))
            return False

        return True
