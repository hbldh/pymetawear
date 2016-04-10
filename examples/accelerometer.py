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
from ctypes import cast, POINTER, c_float

from pymetawear.client import discover_devices, MetaWearClient, libmetawear
from pymetawear.mbientlab.metawear.core import CartesianFloat, DataTypeId, FnDataPtr


print("Discovering nearby MetaWear boards...")
metawear_devices = discover_devices(timeout=2)
if len(metawear_devices) < 1:
    raise ValueError("No MetaWear boards could be detected.")
else:
    address = metawear_devices[0][0]

c = MetaWearClient(str(address), 'pybluez', debug=True)
print("New client created: {0}".format(c))

def acc_callback(data):
    if (data.contents.type_id == DataTypeId.CARTESIAN_FLOAT):
        data_ptr = cast(data.contents.value, POINTER(CartesianFloat))
        print("X: {0}, Y: {1}, Z: {2}".format(int(data_ptr.contents.voltage),
                                              int(data_ptr.contents.charge)))
    else:
        raise RuntimeError('Incorrect data type id: ' + str(data.contents.type_id))

_acc_callback = FnDataPtr(acc_callback)

print("Getting accelerometer data signal...")
acc_signal = libmetawear.mbl_mw_acc_get_acceleration_data_signal(c.board)

print("Write accelerometer settings...")
libmetawear.mbl_mw_acc_set_odr(c.board, c_float(200.0))
libmetawear.mbl_mw_acc_set_range(c.board, c_float(200.0))
libmetawear.mbl_mw_acc_write_acceleration_config(c.board)

print("Start acc on board...")
libmetawear.mbl_mw_acc_start(c.board)
print("Enable acc sampling on board...")
libmetawear.mbl_mw_acc_enable_acceleration_sampling(c.board)

print("Subscribing to accelerometer signal...")
libmetawear.mbl_mw_datasignal_subscribe(acc_signal, _acc_callback)

print("Waiting for update...")
time.sleep(20.0)

c.disconnect()
