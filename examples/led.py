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

from ctypes import byref

from pymetawear.client import discover_devices, MetaWearClient, libmetawear
from pymetawear.mbientlab.metawear.peripheral import Led


print("Discovering nearby MetaWear boards...")
metawear_devices = discover_devices(timeout=2)
if len(metawear_devices) < 1:
    raise ValueError("No MetaWear boards could be detected.")
else:
    address = metawear_devices[0][0]

c = MetaWearClient(str(address), debug=True)
print("New client created: {0}".format(c))

print("Blinking 10 times with green LED...")
pattern = Led.Pattern(repeat_count=10)
libmetawear.mbl_mw_led_load_preset_pattern(byref(pattern), Led.PRESET_BLINK)
libmetawear.mbl_mw_led_write_pattern(c.board, byref(pattern), Led.COLOR_GREEN)
libmetawear.mbl_mw_led_play(c.board)

time.sleep(5.0)

c.disconnect()
