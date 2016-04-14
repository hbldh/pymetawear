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

c = MetaWearClient(str(address), 'pybluez', debug=False)
print("New client created: {0}".format(c))

def acc_callback(data):
    if (data.contents.type_id == DataTypeId.CARTESIAN_FLOAT):
        data_ptr = cast(data.contents.value, POINTER(CartesianFloat))
        print("X: {0}, Y: {1}, Z: {2}".format(data_ptr.contents.x,
                                              data_ptr.contents.y,
                                              data_ptr.contents.z))
    else:
        raise RuntimeError('Incorrect data type id: ' +
                           str(data.contents.type_id))

#  noble-device  +7s send LOGGING <Buffer 0b 0b 00>
#  noble-device  +5ms send LOGGING <Buffer 0b 01 01>
#  noble-device  +2ms send ACCELEROMETER <Buffer 03 03 27 03>
#  noble-device  +1ms send ACCELEROMETER <Buffer 03 04 01>
#  noble-device  +0ms send ACCELEROMETER <Buffer 03 02 01 00>
#  noble-device  +1ms send ACCELEROMETER <Buffer 03 0d 04 0a>
#  noble-device  +0ms send ACCELEROMETER <Buffer 03 0a 00 14 14 14>
#  noble-device  +0ms send ACCELEROMETER <Buffer 03 03 27 03>
#  noble-device  +1ms send ACCELEROMETER <Buffer 03 07 07 30 81 0b c0>
#  noble-device  +0ms send ACCELEROMETER <Buffer 03 01 01>


print("Write accelerometer settings...")
libmetawear.mbl_mw_acc_set_odr(c.board, c_float(50.0))
libmetawear.mbl_mw_acc_set_range(c.board, c_float(2.0))
print("Enable logging on board...")
#libmetawear.mbl_mw_logging_start(c.board)
print("Write accelerometer config....")
libmetawear.mbl_mw_acc_write_acceleration_config(c.board)
print("Subscribing to accelerometer signal...")
c.accelerometer_notifications(acc_callback)
print("Enable acc sampling on board...")
libmetawear.mbl_mw_acc_enable_acceleration_sampling(c.board)
print("Start acc on board...")
libmetawear.mbl_mw_acc_start(c.board)

time.sleep(20.0)

print("Unsubscribe to notification...")
c.accelerometer_notifications(None)
print("Stop accelerometer...")
libmetawear.mbl_mw_acc_stop(c.board)
print("Disable accelerometer sampling...")
libmetawear.mbl_mw_acc_disable_acceleration_sampling(c.board)
print("Stop logging...")
#libmetawear.mbl_mw_logging_stop(c.board)

time.sleep(5.0)

c.disconnect()
