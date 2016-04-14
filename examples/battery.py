#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:mod:`battery`
==================

Created by hbldh <henrik.blidh@nedomkull.com>
Created on 2016-04-02

"""

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import

import time
from ctypes import cast, POINTER, c_uint, c_long
from pymetawear.client import discover_devices, MetaWearClient, libmetawear
from pymetawear.mbientlab.metawear.core import DataTypeId, BatteryState, FnDataPtr

print("WARNING! Incomplete example!")

print("Discovering nearby MetaWear boards...")
metawear_devices = discover_devices(timeout=2)
if len(metawear_devices) < 1:
    raise ValueError("No MetaWear boards could be detected.")
else:
    address = metawear_devices[0][0]

c = MetaWearClient(str(address), 'pygatt', debug=True)
print("New client created: {0}".format(c))

def battery_callback(data):
    if data.contents.type_id == DataTypeId.BATTERY_STATE:
        data_ptr = cast(data.contents.value, POINTER(BatteryState))
        print("Voltage: {0}, Charge: {1}".format(int(data_ptr.contents.voltage),
                                                 int(data_ptr.contents.charge)))
    else:
        raise RuntimeError('Incorrect data type id: ' + str(data.contents.type_id))
_battery_callback = FnDataPtr(battery_callback)

print("Getting battery state data signal...")
# Use long to hold pointer address
libmetawear.mbl_mw_settings_get_battery_state_data_signal.restype= c_long
battery_signal = libmetawear.mbl_mw_settings_get_battery_state_data_signal(c.board)
print(type(battery_signal), battery_signal)

print("Subscribing to battery state...")
libmetawear.mbl_mw_datasignal_subscribe(battery_signal, _battery_callback)
print("Waiting for update...")

print("Reading battery state...")
libmetawear.mbl_mw_settings_read_battery_state(c.board)

time.sleep(5.0)

c.disconnect()
