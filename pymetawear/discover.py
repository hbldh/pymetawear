#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
discover
-----------

:copyright: 2016-11-29 by hbldh <henrik.blidh@nedomkull.com>

"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import os
import signal
import subprocess
import time

from pymetawear.exceptions import PyMetaWearException

try:
    input_fcn = raw_input
except NameError:
    input_fcn = input


def discover_devices(timeout=5):
    """Discover Bluetooth Low Energy Devices nearby on Linux

    Using ``hcitool`` from Bluez in subprocess, which requires root privileges.
    However, ``hcitool`` can be allowed to do scan without elevated permission.

    Install linux capabilities manipulation tools:

    .. code-block:: bash

        $ sudo apt-get install libcap2-bin

    Sets the missing capabilities on the executable quite like the setuid bit:

    .. code-block:: bash

        $ sudo setcap 'cap_net_raw,cap_net_admin+eip' `which hcitool`

    **References:**

    * `StackExchange, hcitool without sudo <https://unix.stackexchange.com/questions/96106/bluetooth-le-scan-as-non-root>`_
    * `StackOverflow, hcitool lescan with timeout <https://stackoverflow.com/questions/26874829/hcitool-lescan-will-not-print-in-real-time-to-a-file>`_

    :param int timeout: Duration of scanning.
    :return: List of tuples with `(address, name)`.
    :rtype: list

    """
    p = subprocess.Popen(["hcitool", "lescan"], stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    time.sleep(timeout)
    os.kill(p.pid, signal.SIGINT)
    out, err = p.communicate()
    if len(out) == 0 and len(err) > 0:
        if err == b'Set scan parameters failed: Operation not permitted\n':
            raise PyMetaWearException("Missing capabilites for hcitool!")
        if err == b'Set scan parameters failed: Input/output error\n':
            raise PyMetaWearException("Could not perform scan.")
    ble_devices = list(set([tuple(x.split(' ')) for x in
                            filter(None, out.decode('utf8').split('\n')[1:])]))
    filtered_devices = {}
    for d in ble_devices:
        if d[0] not in filtered_devices:
            filtered_devices[d[0]] = d[1]
        else:
            if filtered_devices.get(d[0]) == '(unknown)':
                filtered_devices[d[0]] = d[1]

    return [(k, v) for k, v in filtered_devices.items()]


def select_device(timeout=3):
    """Run `discover_devices` and display a list to select from.

    :param int timeout: Duration of scanning.
    :return: The selected device's address.
    :rtype: str

    """
    print("Discovering nearby Bluetooth Low Energy devices...")
    ble_devices = discover_devices(timeout=timeout)
    if len(ble_devices) > 1:
        for i, d in enumerate(ble_devices):
            print("[{0}] - {1}: {2}".format(i + 1, *d))
        s = input("Which device do you want to connect to? ")
        if int(s) <= (i + 1):
            address = ble_devices[int(s) - 1][0]
        else:
            raise ValueError("Incorrect selection. Aborting...")
    elif len(ble_devices) == 1:
        address = ble_devices[0][0]
        print("Found only one device: {0}: {1}.".format(*ble_devices[0][::-1]))
    else:
        raise ValueError("Did not detect any BLE devices.")
    return address
