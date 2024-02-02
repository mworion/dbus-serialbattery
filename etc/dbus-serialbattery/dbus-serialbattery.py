#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
from typing import Union
from time import sleep
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import GLib as gobject
from dbushelper import DbusHelper
from utils import logger
import utils
from battery import Battery
from seplos import Seplos

supported_bms_types = [
    {"bms": Seplos, "baud": 19200},
]


def poll_battery(loop):
    helper.publish_battery(loop)
    return True


def get_battery(_port) -> Union[Battery, None]:
    # all the different batteries the driver support and need to test for
    # try to establish communications with the battery 3 times, else exit
    retry = 1
    retries = 3
    while retry <= retries:
        logger.info(
            "-- Testing BMS: " + str(retry) + " of " + str(retries) + " rounds"
        )
        # create a new battery object that can read the battery and run
        # connection test
        for test in expected_bms_types:
            # noinspection PyBroadException
            try:
                logger.info(
                    "Testing "
                    + test["bms"].__name__
                    + (
                        ' at address "'
                        + utils.bytearray_to_string(test["address"])
                        + '"'
                        if "address" in test
                        else ""
                    )
                )
                batteryClass = test["bms"]
                baud = test["baud"]
                battery: Battery = batteryClass(
                    port=_port, baud=baud, address=test.get("address")
                )
                if battery.test_connection() and battery.validate_data():
                    logger.info(
                        "Connection established to " + battery.__class__.__name__
                    )
                    return battery
            except KeyboardInterrupt:
                return None
            except Exception:
                (
                    exception_type,
                    exception_object,
                    exception_traceback,
                ) = sys.exc_info()
                file = exception_traceback.tb_frame.f_code.co_filename
                line = exception_traceback.tb_lineno
                logger.error(
                    f"Exception occurred: {repr(exception_object)} of type {exception_type} in {file} line #{line}"
                )
                # Ignore any malfunction test_function()
                pass
        retry += 1
        sleep(0.5)

    return None


def get_port() -> str:
    # Get the port we need to use from the argument
    if len(sys.argv) > 1:
        port = sys.argv[1]
        if port not in utils.EXCLUDED_DEVICES:
            return port
        else:
            logger.debug(
                "Stopping dbus-serialbattery: "
                + str(port)
                + " is excluded trough the config file"
            )
            sleep(60)
            sys.exit(0)
    else:
        # just for MNB-SPI
        logger.info("No Port needed")
        return "/dev/ttyUSB9"


def main():

    port = get_port()
    sleep(16)
    battery = get_battery(port)

    # exit if no battery could be found
    if battery is None:
        logger.error("ERROR >>> No battery connection at " + port)
        sys.exit(1)

    battery.log_settings()

    # Have a mainloop, so we can send/receive asynchronous calls to and from dbus
    DBusGMainLoop(set_as_default=True)
    mainloop = gobject.MainLoop()

    # Get the initial values for the battery used by setup_vedbus
    helper = DbusHelper(battery)

    if not helper.setup_vedbus():
        logger.error("ERROR >>> Problem with battery set up at " + port)
        sys.exit(1)

    # try using active callback on this battery
    if not battery.use_callback(lambda: poll_battery(mainloop)):
        # if not possible, poll the battery every poll_interval milliseconds
        gobject.timeout_add(battery.poll_interval, lambda: poll_battery(mainloop))

    # Run the main loop
    try:
        mainloop.run()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    logger.info('Starting dbus-serialbattery')
    logger.info(f'Version + {str(utils.DRIVER_VERSION)}')
    main()
