#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:mod:`gyroscope`
===============

Created by hbldh <henrik.blidh@nedomkull.com>
Created on 2016-04-26

"""

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import

import time
import platform
from ctypes import cast, POINTER, c_float, c_long

from pymetawear.client import MetaWearClient, libmetawear, discover_devices
from pymetawear.exceptions import PyMetaWearException
from pymetawear.mbientlab.metawear.core import \
    CartesianFloat, DataTypeId, Fn_DataPtr


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
c = MetaWearClient(str(address), 'pygatt', debug=True)
print("New client created: {0}".format(c))


def _callback(data):
    """Handle a (x,y,z) gyroscope tuple."""
    if data.contents.type_id == DataTypeId.CARTESIAN_FLOAT:
        data_ptr = cast(data.contents.value, POINTER(CartesianFloat))
        print("X: {0}, Y: {1}, Z: {2}".format(*(data_ptr.contents.x,
                                     data_ptr.contents.y,
                                     data_ptr.contents.z)))
    else:
        raise PyMetaWearException('Incorrect data type id: ' +
            str(data.contents.type_id))
the_callback = Fn_DataPtr(_callback)


print("Set gyroscope settings...")
libmetawear.mbl_mw_gyro_bmi160_set_odr(c.board, 9)
libmetawear.mbl_mw_gyro_bmi160_set_range(c.board, 1)
print("Write gyroscope config....")
libmetawear.mbl_mw_gyro_bmi160_write_config(c.board)
print("Subscribing to gyroscope signal...")
if platform.architecture()[0] == '64bit':
    libmetawear.mbl_mw_gyro_bmi160_get_rotation_data_signal.restype = c_long
    data_signal = c_long(libmetawear.mbl_mw_gyro_bmi160_get_rotation_data_signal(c.board))
else:
    data_signal = libmetawear.mbl_mw_gyro_bmi160_get_rotation_data_signal(c.board)
libmetawear.mbl_mw_datasignal_subscribe(data_signal, the_callback)
print("Enable gyro sampling on board...")
libmetawear.mbl_mw_gyro_bmi160_enable_rotation_sampling(c.board)
print("Start gyro on board...")
libmetawear.mbl_mw_gyro_bmi160_start(c.board)

time.sleep(20.0)

print("Stop gyroscope...")
libmetawear.mbl_mw_gyro_bmi160_stop(c.board)
print("Disable gyroscope sampling...")
libmetawear.mbl_mw_gyro_bmi160_disable_rotation_sampling(c.board)
print("Unsubscribe to notification...")
libmetawear.mbl_mw_datasignal_unsubscribe(data_signal)



time.sleep(5.0)

c.disconnect()
