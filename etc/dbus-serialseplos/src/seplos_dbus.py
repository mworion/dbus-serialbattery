# -*- coding: utf-8 -*-
import sys
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import GLib as gobject
from seplos_dbus_helper import DbusHelper
from seplos_pack import SeplosPack


BATTERY_PACKS = 2
BATTERY_PORTS = ['/dev/tty.usbserial-B0019Z73',
                 '/dev/tty.usbserial-B001AA8J',
                 'ttyUSB0',
                 'ttyUSB1',
                 'ttyUSB2',
                 'ttyUSB3',
                 ]


def main():
    """
    """
    seplos_pack = SeplosPack(number_packs=BATTERY_PACKS, battery_ports=BATTERY_PORTS)
    if len(seplos_pack.seplos_batteries) == 0:
        sys.exit(1)

    DBusGMainLoop(set_as_default=True)
    loop = gobject.MainLoop()
    helper = DbusHelper(seplos_pack)
    if not helper.setup_vedbus():
        sys.exit(1)

    gobject.timeout_add(seplos_pack.POLL_INTERVAL, lambda: helper.publish_battery(loop))

    try:
        loop.run()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
