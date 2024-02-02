# -*- coding: utf-8 -*-
from typing import Union, List, Callable
from utils import logger
import utils
import logging
from abc import ABC, abstractmethod


class Protection(object):
    """
    This class holds Warning and alarm states for different types of Checks
    They are of type integer, 2 represents an Alarm, 1 a Warning, 0 if
    everything is fine
    """

    ALARM = 2
    WARNING = 1
    OK = 0

    def __init__(self):
        self.voltage_high: int = None
        self.voltage_low: int = None
        self.voltage_cell_low: int = None
        self.soc_low: int = None
        self.current_over: int = None
        self.current_under: int = None
        self.cell_imbalance: int = None
        self.internal_failure: int = None
        self.temp_high_charge: int = None
        self.temp_low_charge: int = None
        self.temp_high_discharge: int = None
        self.temp_low_discharge: int = None
        self.temp_high_internal: int = None


class Cell:
    """
    This class holds information about a single Cell
    """

    voltage = None
    balance = None
    temp = None

    def __init__(self, balance):
        self.balance = balance


class Battery(ABC):
    """
    This Class is the abstract baseclass for all batteries. For each BMS this class needs to be extended
    and the abstract methods need to be implemented. The main program in dbus-serialbattery.py will then
    use the individual implementations as type Battery and work with it.
    """

    def __init__(self, port, baud, address):
        self.port = port
        self.baud_rate = baud
        self.role = "battery"
        self.type = "Generic"
        self.poll_interval = 1000
        self.online = True
        self.hardware_version = None
        self.cell_count = None
        # max battery charge/discharge current
        self.max_battery_charge_current = None
        self.max_battery_discharge_current = None
        self.has_settings = 0

        # fetched from the BMS from a field where the user can input a custom string
        # only if available
        self.custom_field = None

        self.init_values()

    def init_values(self):
        """
        Used to reset values, if battery unexpectly disconnects
        """
        self.voltage = None
        self.current = None
        self.current_avg = None
        self.current_avg_lst = []
        self.capacity_remain = None
        self.capacity = None
        self.cycles = None
        self.total_ah_drawn = None
        self.production = None
        self.protection = Protection()
        self.version = None
        self.soc = None
        self.time_to_soc_update = 0
        self.charge_fet = None
        self.discharge_fet = None
        self.balance_fet = None
        self.temp_sensors = None
        self.temp1 = None
        self.temp2 = None
        self.temp3 = None
        self.temp4 = None
        self.temp_mos = None
        self.cells: List[Cell] = []
        self.control_charging = None
        self.control_voltage = None
        self.soc_reset_requested = False
        self.soc_reset_last_reached = 0
        self.soc_reset_battery_voltage = None
        self.max_battery_voltage = None
        self.min_battery_voltage = None
        self.allow_max_voltage = True
        self.max_voltage_start_time = None
        self.transition_start_time = None
        self.control_voltage_at_transition_start = None
        self.charge_mode = None
        self.charge_mode_debug = ""
        self.charge_limitation = None
        self.discharge_limitation = None
        self.linear_cvl_last_set = 0
        self.linear_ccl_last_set = 0
        self.linear_dcl_last_set = 0
        self.control_current = None
        self.control_previous_total = None
        self.control_previous_max = None
        self.control_discharge_current = None
        self.control_charge_current = None
        self.control_allow_charge = None
        self.control_allow_discharge = None

    @abstractmethod
    def test_connection(self) -> bool:
        """
        This abstract method needs to be implemented for each BMS. It shoudl return true if a connection
        to the BMS can be established, false otherwise.
        :return: the success state
        """
        # Each driver must override this function to test if a connection can be made
        # return false when failed, true if successful
        return False

    def unique_identifier(self) -> str:
        """
        Used to identify a BMS when multiple BMS are connected
        If not provided by the BMS/driver then the hardware version and capacity is used,
        since it can be changed by small amounts to make a battery unique.
        On +/- 5 Ah you can identify 11 batteries
        """
        string = (
            "".join(filter(str.isalnum, str(self.hardware_version))) + "_"
            if self.hardware_version is not None and self.hardware_version != ""
            else ""
        )
        string += str(self.capacity) + "Ah"
        return string

    def connection_name(self) -> str:
        return "Serial " + self.port

    def custom_name(self) -> str:
        """
        Check if the custom name is present in the config file, else return default name
        """
        if len(utils.CUSTOM_BATTERY_NAMES) > 0:
            for name in utils.CUSTOM_BATTERY_NAMES:
                tmp = name.split(":")
                if tmp[0].strip() == self.port:
                    return tmp[1].strip()
        else:
            return "SerialBattery(" + self.type + ")"

    def product_name(self) -> str:
        return "SerialBattery(" + self.type + ")"

    @abstractmethod
    def get_settings(self) -> bool:
        """
        Each driver must override this function to read/set the battery settings
        It is called once after a successful connection by DbusHelper.setup_vedbus()
        Values:  battery_type, version, hardware_version, min_battery_voltage, max_battery_voltage,
        MAX_BATTERY_CHARGE_CURRENT, MAX_BATTERY_DISCHARGE_CURRENT, cell_count, capacity

        :return: false when fail, true if successful
        """
        return False

    def use_callback(self, callback: Callable) -> bool:
        """
        Each driver may override this function to indicate whether it is
        able to provide value updates on its own.

        :return: false when battery cannot provide updates by itself and will be polled
                 every poll_interval milliseconds for new values
                 true if callable should be used for updates as they arrive from the battery
        """
        return False

    @abstractmethod
    def refresh_data(self) -> bool:
        """
        Each driver must override this function to read battery data and populate this class
        It is called each poll just before the data is published to vedbus

        :return:  false when fail, true if successful
        """
        return False

    def to_temp(self, sensor: int, value: float) -> None:
        """
        Keep the temp value between -20 and 100 to handle sensor issues or no data.
        The BMS should have already protected before those limits have been reached.

        :param sensor: temperature sensor number
        :param value: the sensor value
        :return:
        """
        if sensor == 0:
            self.temp_mos = min(max(value, -20), 100)
        if sensor == 1:
            self.temp1 = min(max(value, -20), 100)
        if sensor == 2:
            self.temp2 = min(max(value, -20), 100)
        if sensor == 3:
            self.temp3 = min(max(value, -20), 100)
        if sensor == 4:
            self.temp4 = min(max(value, -20), 100)

    def get_min_cell(self) -> int:
        min_voltage = 9999
        min_cell = None
        if len(self.cells) == 0 and hasattr(self, "cell_min_no"):
            return self.cell_min_no

        for c in range(min(len(self.cells), self.cell_count)):
            if (
                self.cells[c].voltage is not None
                and min_voltage > self.cells[c].voltage
            ):
                min_voltage = self.cells[c].voltage
                min_cell = c
        return min_cell

    def get_max_cell(self) -> int:
        max_voltage = 0
        max_cell = None
        if len(self.cells) == 0 and hasattr(self, "cell_max_no"):
            return self.cell_max_no

        for c in range(min(len(self.cells), self.cell_count)):
            if (
                self.cells[c].voltage is not None
                and max_voltage < self.cells[c].voltage
            ):
                max_voltage = self.cells[c].voltage
                max_cell = c
        return max_cell

    def get_min_cell_desc(self) -> Union[str, None]:
        cell_no = self.get_min_cell()
        return cell_no if cell_no is None else "C" + str(cell_no + 1)

    def get_max_cell_desc(self) -> Union[str, None]:
        cell_no = self.get_max_cell()
        return cell_no if cell_no is None else "C" + str(cell_no + 1)

    def get_cell_voltage(self, idx) -> Union[float, None]:
        if idx >= min(len(self.cells), self.cell_count):
            return None
        return self.cells[idx].voltage

    def get_cell_balancing(self, idx) -> Union[int, None]:
        if idx >= min(len(self.cells), self.cell_count):
            return None
        if self.cells[idx].balance is not None and self.cells[idx].balance:
            return 1
        return 0

    def get_capacity_remain(self) -> Union[float, None]:
        if self.capacity_remain is not None:
            return self.capacity_remain
        if self.capacity is not None and self.soc is not None:
            return self.capacity * self.soc / 100
        return None

    def get_timeToSoc(self, socnum, crntPrctPerSec, onlyNumber=False) -> str:
        if self.current > 0:
            diffSoc = socnum - self.soc
        else:
            diffSoc = self.soc - socnum

        """
        calculate only positive SoC points, since negative points have no sense
        when charging only points above current SoC are shown
        when discharging only points below current SoC are shown
        """
        if diffSoc < 0:
            return None

        ttgStr = None
        if self.soc != socnum and (diffSoc > 0 or utils.TIME_TO_SOC_INC_FROM is True):
            secondstogo = int(diffSoc / crntPrctPerSec)
            ttgStr = ""

            if onlyNumber or utils.TIME_TO_SOC_VALUE_TYPE & 1:
                ttgStr += str(secondstogo)
                if not onlyNumber and utils.TIME_TO_SOC_VALUE_TYPE & 2:
                    ttgStr += " ["
            if not onlyNumber and utils.TIME_TO_SOC_VALUE_TYPE & 2:
                ttgStr += self.get_secondsToString(secondstogo)

                if utils.TIME_TO_SOC_VALUE_TYPE & 1:
                    ttgStr += "]"

        return ttgStr

    def get_secondsToString(self, timespan, precision=3) -> str:
        """
        Transforms seconds to a string in the format: 1d 1h 1m 1s (Victron Style)
        :param precision:
        0 = 1d
        1 = 1d 1h
        2 = 1d 1h 1m
        3 = 1d 1h 1m 1s

        This was added, since timedelta() returns strange values, if time is negative
        e.g.: seconds: -70245
              --> timedelta output: -1 day, 4:29:15
              --> calculation: -1 day + 4:29:15
              --> real value -19:30:45
        """
        tmp = "" if timespan >= 0 else "-"
        timespan = abs(timespan)

        m, s = divmod(timespan, 60)
        h, m = divmod(m, 60)
        d, h = divmod(h, 24)

        tmp += (str(d) + "d ") if d > 0 else ""
        tmp += (str(h) + "h ") if precision >= 1 and h > 0 else ""
        tmp += (str(m) + "m ") if precision >= 2 and m > 0 else ""
        tmp += (str(s) + "s ") if precision == 3 and s > 0 else ""

        return tmp.rstrip()

    def get_min_cell_voltage(self) -> Union[float, None]:
        min_voltage = None
        if hasattr(self, "cell_min_voltage"):
            min_voltage = self.cell_min_voltage

        if min_voltage is None:
            try:
                min_voltage = min(
                    c.voltage for c in self.cells if c.voltage is not None
                )
            except ValueError:
                pass
        return min_voltage

    def get_max_cell_voltage(self) -> Union[float, None]:
        max_voltage = None
        if hasattr(self, "cell_max_voltage"):
            max_voltage = self.cell_max_voltage

        if max_voltage is None:
            try:
                max_voltage = max(
                    c.voltage for c in self.cells if c.voltage is not None
                )
            except ValueError:
                pass
        return max_voltage

    def get_balancing(self) -> int:
        for c in range(min(len(self.cells), self.cell_count)):
            if self.cells[c].balance is not None and self.cells[c].balance:
                return 1
        return 0

    def get_temperatures(self) -> Union[List[float], None]:
        temperatures = [self.temp1, self.temp2, self.temp3, self.temp4]
        result = [(t, i) for (t, i) in enumerate(temperatures) if t is not None]
        if not result:
            return None

    def get_temp(self) -> Union[float, None]:
        try:
            if utils.TEMP_BATTERY == 1:
                return self.temp1
            elif utils.TEMP_BATTERY == 2:
                return self.temp2
            elif utils.TEMP_BATTERY == 3:
                return self.temp3
            elif utils.TEMP_BATTERY == 4:
                return self.temp4
            else:
                temps = [
                    t
                    for t in [self.temp1, self.temp2, self.temp3, self.temp4]
                    if t is not None
                ]
                n = len(temps)
                if not temps or n == 0:
                    return None
                data = sorted(temps)
                if n % 2 == 1:
                    return data[n // 2]
                else:
                    i = n // 2
                    return (data[i - 1] + data[i]) / 2
        except TypeError:
            return None

    def get_min_temp(self) -> Union[float, None]:
        try:
            temps = [
                t
                for t in [self.temp1, self.temp2, self.temp3, self.temp4]
                if t is not None
            ]
            if not temps:
                return None
            return min(temps)
        except TypeError:
            return None

    def get_min_temp_id(self) -> Union[str, None]:
        try:
            temps = [
                (t, i)
                for i, t in enumerate([self.temp1, self.temp2, self.temp3, self.temp4])
                if t is not None
            ]
            if not temps:
                return None
            index = min(temps)[1]
            if index == 0:
                return utils.TEMP_1_NAME
            if index == 1:
                return utils.TEMP_2_NAME
            if index == 2:
                return utils.TEMP_3_NAME
            if index == 3:
                return utils.TEMP_4_NAME
        except TypeError:
            return None

    def get_max_temp(self) -> Union[float, None]:
        try:
            temps = [
                t
                for t in [self.temp1, self.temp2, self.temp3, self.temp4]
                if t is not None
            ]
            if not temps:
                return None
            return max(temps)
        except TypeError:
            return None

    def get_max_temp_id(self) -> Union[str, None]:
        try:
            temps = [
                (t, i)
                for i, t in enumerate([self.temp1, self.temp2, self.temp3, self.temp4])
                if t is not None
            ]
            if not temps:
                return None
            index = max(temps)[1]
            if index == 0:
                return utils.TEMP_1_NAME
            if index == 1:
                return utils.TEMP_2_NAME
            if index == 2:
                return utils.TEMP_3_NAME
            if index == 3:
                return utils.TEMP_4_NAME
        except TypeError:
            return None

    def get_mos_temp(self) -> Union[float, None]:
        if self.temp_mos is not None:
            return self.temp_mos
        else:
            return None

    def validate_data(self) -> bool:
        """
        Used to validate the data received from the BMS.
        If the data is in the thresholds return True,
        else return False since it's very probably not a BMS
        """
        if self.capacity is not None and (self.capacity < 0 or self.capacity > 1000):
            logger.debug(
                "Capacity outside of thresholds (from 0 to 1000): " + str(self.capacity)
            )
            return False
        if self.current is not None and abs(self.current) > 1000:
            logger.debug(
                "Current outside of thresholds (from -1000 to 1000): "
                + str(self.current)
            )
            return False
        if self.voltage is not None and (self.voltage < 0 or self.voltage > 100):
            logger.debug(
                "Voltage outside of thresholds (form 0 to 100): " + str(self.voltage)
            )
            return False
        if self.soc is not None and (self.soc < 0 or self.soc > 100):
            logger.debug("SoC outside of thresholds (from 0 to 100): " + str(self.soc))
            return False

        return True

    def log_cell_data(self) -> bool:
        if logger.getEffectiveLevel() > logging.INFO and len(self.cells) == 0:
            return False

        cell_res = ""
        cell_counter = 1
        for c in self.cells:
            cell_res += "[{0}]{1}V ".format(cell_counter, c.voltage)
            cell_counter = cell_counter + 1
        logger.debug("Cells:" + cell_res)
        return True

    def log_settings(self) -> None:
        cell_counter = len(self.cells)
        logger.info(f"Battery {self.type} connected to dbus from {self.port}")
        logger.info("========== Settings ==========")
        logger.info(
            f"> Connection voltage: {self.voltage}V | Current: {self.current}A | SoC: {self.soc}%"
        )
        logger.info(
            f"> Cell count: {self.cell_count} | Cells populated: {cell_counter}"
        )
        logger.info(f"> LINEAR LIMITATION ENABLE: {utils.LINEAR_LIMITATION_ENABLE}")
        logger.info(
            f"> MAX BATTERY CHARGE CURRENT: {utils.MAX_BATTERY_CHARGE_CURRENT}A | "
            + f"MAX BATTERY DISCHARGE CURRENT: {utils.MAX_BATTERY_DISCHARGE_CURRENT}A"
        )
        if (
            (
                utils.MAX_BATTERY_CHARGE_CURRENT != self.max_battery_charge_current
                or utils.MAX_BATTERY_DISCHARGE_CURRENT
                != self.max_battery_discharge_current
            )
            and self.max_battery_charge_current is not None
            and self.max_battery_discharge_current is not None
        ):
            logger.info(
                f"> MAX BATTERY CHARGE CURRENT: {self.max_battery_charge_current}A | "
                + f"MAX BATTERY DISCHARGE CURRENT: {self.max_battery_discharge_current}A (read from BMS)"
            )
        logger.info(f"> CVCM:     {utils.CVCM_ENABLE}")
        logger.info(
            f"> MIN CELL VOLTAGE: {utils.MIN_CELL_VOLTAGE}V | MAX CELL VOLTAGE: {utils.MAX_CELL_VOLTAGE}V"
        )
        logger.info(
            f"> CCCM CV:  {str(utils.CCCM_CV_ENABLE).ljust(5)} | DCCM CV:  {utils.DCCM_CV_ENABLE}"
        )
        logger.info(
            f"> CCCM T:   {str(utils.CCCM_T_ENABLE).ljust(5)} | DCCM T:   {utils.DCCM_T_ENABLE}"
        )
        logger.info(
            f"> CCCM SOC: {str(utils.CCCM_SOC_ENABLE).ljust(5)} | DCCM SOC: {utils.DCCM_SOC_ENABLE}"
        )
        logger.info(f"Serial Number/Unique Identifier: {self.unique_identifier()}")
        return
