#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:mod:`led`
==================

Created by hbldh <henrik.blidh@nedomkull.com>
Created on 2016-04-02

"""

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import

import time

from pymetawear.client import discover_devices, MetaWearClient

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
        raise ValueError("DId not detect any BLE devices.")
    return address


address = scan_and_select_le_device()
c = MetaWearClient(str(address), debug=True)
print("New client created: {0}".format(c))

print("Blinking 10 times with green LED...")
from ctypes import byref
from pymetawear import libmetawear
from pymetawear.mbientlab.metawear.peripheral import Led

pattern = Led.Pattern(repeat_count=10)
libmetawear.mbl_mw_led_load_preset_pattern(byref(pattern), Led.PRESET_BLINK)
libmetawear.mbl_mw_led_write_pattern(c.board, byref(pattern), Led.COLOR_GREEN)
libmetawear.mbl_mw_led_play(c.board)

time.sleep(5.0)

c.disconnect()
