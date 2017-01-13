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
from __future__ import absolute_import

import time

from pymetawear.client import MetaWearClient
from pymetawear.discover import select_device

address = select_device()
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
