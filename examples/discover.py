#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:mod:`discover`
---------------

:copyright: 2016-08-09 by hbldh <henrik.blidh@swedwise.com>

"""

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import

from pymetawear.client import discover_devices

try:
    input_fcn = raw_input
except NameError:
    input_fcn = input


def scan_and_select_le_device(timeout=3):
    print("Discovering nearby Bluetooth Low Energy devices...")
    ble_devices = discover_devices(timeout=timeout)
    if len(ble_devices) > 1:
        for i, d in enumerate(ble_devices):
            print("[{0}] - {1}: {2}".format(i+1, *d))
        s = input("Which device do you want to connect to? ")
        if int(s) <= (i + 1):
            address = ble_devices[int(s) - 1][0]
        else:
            raise ValueError("Incorrect selection. Aborting...")
    elif len(ble_devices) == 1:
        address = ble_devices[0][0]
    else:
        raise ValueError("Did not detect any BLE devices.")
    return address
