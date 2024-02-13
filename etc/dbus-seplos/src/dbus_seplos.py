# -*- coding: utf-8 -*-
import sys
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import GLib as gobject
from seplos_dbus_helper import DbusHelper
from seplos_pack import SeplosPack
from seplos_utils import logger


def get_port() -> str:
    """
    """
    if len(sys.argv) == 1:
        logger.info(f"Getting port {sys.argv[1]}")
        return sys.argv[1]
    else:
        return ''


def main():
    """
    """
    port = get_port()
    seplos_pack = SeplosPack(battery_port=port)
    if len(seplos_pack.seplos_batteries) == 0:
        sys.exit(1)

    DBusGMainLoop(set_as_default=True)
    loop = gobject.MainLoop()
    helper = DbusHelper(seplos_pack)
    if not helper.setup_vedbus():
        sys.exit(1)

    gobject.timeout_add(seplos_pack.POLL_INTERVAL,
                        lambda: helper.publish_battery_pack(loop))

    try:
        loop.run()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
