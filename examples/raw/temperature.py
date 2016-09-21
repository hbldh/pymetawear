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

from ctypes import POINTER, c_float, cast, c_long, c_uint8
import time
import platform

from pymetawear import libmetawear
from pymetawear.client import discover_devices, MetaWearClient
from pymetawear.mbientlab.metawear.core import DataTypeId, Fn_DataPtr

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


def temperature_callback(data):
    if data.contents.type_id == DataTypeId.FLOAT:
        data_ptr = cast(data.contents.value, POINTER(c_float))
        print("Temperature read: {0:.2f} C".format(data_ptr.contents.value))
    else:
        raise RuntimeError('Incorrect data type id: ' + str(data.contents.type_id))


# On-Die temperature (channel 0) is always present.
channel = 0

# Subscribe to notifications
if platform.architecture()[0] == '64bit':
    libmetawear.mbl_mw_multi_chnl_temp_get_temperature_data_signal.restype = c_long
    data_signal = c_long(
        libmetawear.mbl_mw_multi_chnl_temp_get_temperature_data_signal(
            c.board, channel))
else:
    data_signal = libmetawear.mbl_mw_multi_chnl_temp_get_temperature_data_signal(
        c.board, channel)
fcn_dptr = Fn_DataPtr(temperature_callback)
libmetawear.mbl_mw_datasignal_subscribe(data_signal, fcn_dptr)

for i in range(5):
    libmetawear.mbl_mw_datasignal_read(data_signal)
    time.sleep(1.0)

# Unsubscribe to notifications
libmetawear.mbl_mw_datasignal_unsubscribe(data_signal)

time.sleep(1.0)

c.disconnect()

