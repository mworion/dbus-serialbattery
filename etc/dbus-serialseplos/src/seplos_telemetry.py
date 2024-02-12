# -*- coding: utf-8 -*-
from seplos_protocol import int_from_ascii


class Telemetry(object):
    """
    """
    MIN_CELL_VOLTAGE = 2.5
    MAX_CELL_VOLTAGE = 3.6

    def __init__(self):
        # from pack

        self.cell_voltage = [None] * 16
        self.cell_temperature: float = [None] * 4
        self.ambient_temperature: float = None
        self.components_temperature: float = None
        self.dis_charge_current: float = None
        self.total_pack_voltage: float = None
        self.residual_capacity: float = None
        self.battery_capacity: float = None
        self.soc: float = None
        self.rated_capacity: float = None
        self.cycles: int = None
        self.soh: float = None
        self.port_voltage: float = None

        # calculated

        self.average_cell_voltage: float = None
        self.delta_cell_voltage: float = None
        self.lowest_cell: int = None
        self.lowest_cell_voltage: float = None
        self.highest_cell: int = None
        self.highest_cell_voltage: float = None
        self.min_pack_voltage: float = None
        self.max_pack_voltage: float = None
        self.dis_charge_power: float = None

    def get_lowest_cell(self) -> dict:
        lowest_cell = self.cell_voltage.index(min(self.cell_voltage))
        lowest_cell_voltage = self.cell_voltage[lowest_cell]
        return lowest_cell, lowest_cell_voltage

    def get_highest_cell(self) -> dict:
        highest_cell = self.cell_voltage.index(max(self.cell_voltage))
        highest_cell_voltage = self.cell_voltage[highest_cell]
        return highest_cell, highest_cell_voltage

    def decode_data(self, data) -> None:
        """
        """
        # data offsets
        cell_voltage_offset = 6
        temps_offset = 72
        dis_charge_current_offset = 96
        total_pack_voltage_offset = 100
        residual_capacity_offset = 104
        battery_capacity_offset = 110
        soc_offset = 114
        rated_capacity_offset = 118
        cycles_offset = 122
        soh_offset = 126
        port_voltage_offset = 130
        number_of_cells = int_from_ascii(data=data, offset=4, size=2)

        self.min_pack_voltage = self.MIN_CELL_VOLTAGE * number_of_cells
        self.max_pack_voltage = self.MAX_CELL_VOLTAGE * number_of_cells

        for i in range(number_of_cells):
            voltage = int_from_ascii(data, cell_voltage_offset + i * 4) / 1000
            self.cell_voltage[i] = voltage

        self.average_cell_voltage = round((sum(self.cell_voltage)
                                           / len(self.cell_voltage)), 3)

        self.lowest_cell, self.lowest_cell_voltage = self.get_lowest_cell()
        self.highest_cell, self.highest_cell_voltage = self.get_highest_cell()
        self.delta_cell_voltage = round((self.highest_cell_voltage - self.lowest_cell_voltage), 3)

        for i in range(0, 4):
            temp = (int_from_ascii(data, temps_offset + i * 4) - 2731) / 10
            self.cell_temperature[i] = temp

        self.ambient_temperature = (int_from_ascii(data, temps_offset + 4 * 4) - 2731) / 10
        self.components_temperature = (int_from_ascii(data, temps_offset + 5 * 4) - 2731) / 10
        self.dis_charge_current = int_from_ascii(data, dis_charge_current_offset, signed=True) / 100
        self.total_pack_voltage = int_from_ascii(data, total_pack_voltage_offset) / 100
        self.dis_charge_power = round((self.dis_charge_current * self.total_pack_voltage), 3)
        self.rated_capacity = int_from_ascii(data, rated_capacity_offset) / 100
        self.battery_capacity = int_from_ascii(data, battery_capacity_offset) / 100
        self.residual_capacity = int_from_ascii(data, residual_capacity_offset) / 100
        self.soc = int_from_ascii(data, soc_offset) / 10
        self.cycles = int_from_ascii(data, cycles_offset)
        self.soh = int_from_ascii(data, soh_offset) / 10
        self.port_voltage = int_from_ascii(data, port_voltage_offset) / 100
