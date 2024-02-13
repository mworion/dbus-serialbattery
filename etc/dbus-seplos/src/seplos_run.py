# -*- coding: utf-8 -*-
import time
import sys
from seplos_battery import SeplosBattery
from seplos_pack import SeplosPack


BATTERY_PACKS = 2
BATTERY_PORTS = ['/dev/ttyUSB0',
                 '/dev/ttyUSB1',
                 ]


def show_data(battery: SeplosBattery):
    """
    """
    print(battery.type)
    battery.refresh_data()
    print(battery.telemetry.cell_voltage)
    print(battery.alarm.cell_equalization)


def main():
    print('Start')
    seplos_pack = SeplosPack(number_packs=BATTERY_PACKS, battery_ports=BATTERY_PORTS)

    if len(seplos_pack.seplos_batteries) != BATTERY_PACKS:
        sys.exit(1)

    for i in range(20):
        for seplos_battery in seplos_pack.seplos_batteries:
            show_data(seplos_battery)
        time.sleep(1)

    for seplos_battery in seplos_pack.seplos_batteries:
        seplos_battery.comm.serial_if.close()

    print('Batteries in pack:', len(seplos_pack.seplos_batteries))
    print('Done')


if __name__ == "__main__":
    main()
