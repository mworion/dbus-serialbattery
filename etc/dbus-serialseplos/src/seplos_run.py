# -*- coding: utf-8 -*-

from seplos_battery import SeplosBattery
from seplos_pack import SeplosPack


def show_data(battery: SeplosBattery):
    """
    """
    print(battery.type)
    battery.refresh_data()
    print(battery.telemetry.cell_voltage)
    print(battery.alarm.cell_equalization)


def main():
    print('Start')
    seplos_pack = SeplosPack()
    for seplos_battery in seplos_pack.seplos_batteries:
        show_data(seplos_battery)

    print('Batteries in pack:', len(seplos_pack.seplos_batteries))
    print('Done')


if __name__ == "__main__":
    main()
