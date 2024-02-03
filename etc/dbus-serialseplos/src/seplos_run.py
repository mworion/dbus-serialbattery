# -*- coding: utf-8 -*-

from seplos_battery import SeplosBattery


def main():
    seplos_battery = SeplosBattery()

    val_telemetry = seplos_battery.comm[0].read_telemetry_data()
    print(val_telemetry)
    seplos_battery.telemetry.decode(val_telemetry)
    print(seplos_battery.telemetry.cell_voltage)

    val_alarm = seplos_battery.comm[0].read_alarm_data()
    print(val_alarm)
    seplos_battery.alarm.decode(val_alarm)
    print(seplos_battery.alarm.cell_equalization)

    val_telemetry = seplos_battery.comm[1].read_telemetry_data()
    print(val_telemetry)
    seplos_battery.telemetry.decode(val_telemetry)
    print(seplos_battery.telemetry.cell_voltage)

    val_alarm = seplos_battery.comm[1].read_alarm_data()
    print(val_alarm)
    seplos_battery.alarm.decode(val_alarm)
    print(seplos_battery.alarm.cell_equalization)


if __name__ == "__main__":
    main()
