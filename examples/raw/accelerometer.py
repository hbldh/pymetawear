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
import platform
from ctypes import cast, POINTER, c_float, c_long

from pymetawear.client import discover_devices, MetaWearClient, libmetawear
from pymetawear.exceptions import PyMetaWearException
from pymetawear.mbientlab.metawear.core import CartesianFloat, DataTypeId, Fn_DataPtr
from pymetawear.client import MetaWearClient


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

address = scan_and_select_le_device()
c = MetaWearClient(str(address), 'pygatt', debug=True)
print("New client created: {0}".format(c))


def acc_callback(data):
    """Handle a (x,y,z) accelerometer tuple."""
    if data.contents.type_id == DataTypeId.CARTESIAN_FLOAT:
        data_ptr = cast(data.contents.value, POINTER(CartesianFloat))
        print("X: {0}, Y: {1}, Z: {2}".format(*(data_ptr.contents.x,
                                     data_ptr.contents.y,
                                     data_ptr.contents.z)))
    else:
        raise PyMetaWearException('Incorrect data type id: ' +
            str(data.contents.type_id))
_acc_callback = Fn_DataPtr(acc_callback)


print("Write accelerometer settings...")
libmetawear.mbl_mw_acc_set_odr(c.board, c_float(50.0))
libmetawear.mbl_mw_acc_set_range(c.board, c_float(4.0))
print("Write accelerometer config....")
libmetawear.mbl_mw_acc_write_acceleration_config(c.board)

print("Subscribing to accelerometer signal...")
if platform.architecture()[0] == '64bit':
    libmetawear.mbl_mw_acc_get_acceleration_data_signal.restype = c_long    
    data_signal = c_long(libmetawear.mbl_mw_acc_get_acceleration_data_signal(c.board))
else:
    data_signal = libmetawear.mbl_mw_acc_get_acceleration_data_signal(c.board)
libmetawear.mbl_mw_datasignal_subscribe(data_signal, _acc_callback)
print("Enable acc sampling on board...")
libmetawear.mbl_mw_acc_enable_acceleration_sampling(c.board)
print("Start acc on board...")
libmetawear.mbl_mw_acc_start(c.board)

time.sleep(10.0)


print("Stop accelerometer...")
libmetawear.mbl_mw_acc_stop(c.board)
print("Disable accelerometer sampling...")
libmetawear.mbl_mw_acc_disable_acceleration_sampling(c.board)
print("Unsubscribe to notification...")
libmetawear.mbl_mw_datasignal_unsubscribe(data_signal)

time.sleep(5.0)

c.disconnect()
