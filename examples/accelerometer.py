#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:mod:`accelerometer`
==================

Created by hbldh <henrik.blidh@nedomkull.com>
Created on 2016-04-10

"""

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import

import time
from ctypes import cast, POINTER, c_float, c_long

from pymetawear.client import discover_devices, MetaWearClient, libmetawear
from pymetawear.mbientlab.metawear.core import CartesianFloat, DataTypeId, FnDataPtr

print("Warning: Incomplete example!")

print("Discovering nearby MetaWear boards...")
metawear_devices = discover_devices(timeout=2)
if len(metawear_devices) < 1:
    raise ValueError("No MetaWear boards could be detected.")
else:
    address = metawear_devices[0][0]

c = MetaWearClient(str(address), 'pybluez', debug=True)
print("New client created: {0}".format(c))


def acc_callback(data):
    """Handle a (x,y,z) accelerometer tuple."""
    print("X: {0}, Y: {1}, Z: {2}".format(*data))


print("Write accelerometer settings...")
c.accelerometer.set_settings(data_rate=200.0, data_range=2)
print("Subscribing to accelerometer signal notifications...")
c.accelerometer.notifications(acc_callback)

time.sleep(20.0)

print("Unsubscribe to notification...")
c.accelerometer.notifications(None)

time.sleep(5.0)

c.disconnect()
