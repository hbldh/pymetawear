#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
discover
-----------------------------------

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


def scan_and_select_le_device():
    print("Discovering nearby Bluetooth Low Energy devices...")
    ble_devices = discover_devices(timeout=2)
    if len(ble_devices) > 1:
        for i, d in enumerate(ble_devices):
            print("[{0}] - {1}: {2}".format(i+1, *d))
        s = input("Which device do you want to connect to? ")
        if s.isdigit() and int(s) <= i + 1:
            address = ble_devices[int(s) - 1][0]
        else:
            raise ValueError("Incorrect selection. Aborting...")
    else:
        address = ble_devices[0][0]
    return address
