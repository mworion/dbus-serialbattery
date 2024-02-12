# -*- coding: utf-8 -*-

from seplos_battery import SeplosBattery
from seplos_pack import SeplosPack


BATTERY_PACKS = 2
BATTERY_PORTS = ['/dev/tty.usbserial-B0019Z73',
                 '/dev/tty.usbserial-B001AA8J',
                 '/dev/tty.usbserial-VE6NMUVK',
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
    for seplos_battery in seplos_pack.seplos_batteries:
        show_data(seplos_battery)

    print('Batteries in pack:', len(seplos_pack.seplos_batteries))
    print('Done')


if __name__ == "__main__":
    main()
