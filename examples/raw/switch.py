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

from ctypes import POINTER, c_uint, cast, c_long
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


def switch_callback(data):
    if (data.contents.type_id == DataTypeId.UINT32):
        data_ptr = cast(data.contents.value, POINTER(c_uint))
        if data_ptr.contents.value == 1:
            print("Switch pressed!")
        elif data_ptr.contents.value == 0:
            print("Switch released!")
        else:
            raise ValueError("Incorrect data returned.")
    else:
        raise RuntimeError('Incorrect data type id: ' + str(data.contents.type_id))


# Subscribe
if platform.architecture()[0] == '64bit':
    libmetawear.mbl_mw_switch_get_state_data_signal.restype = c_long
    data_signal = c_long(libmetawear.mbl_mw_switch_get_state_data_signal(c.board))
else:
    data_signal = libmetawear.mbl_mw_switch_get_state_data_signal(c.board)
fcn_dptr = Fn_DataPtr(switch_callback)
libmetawear.mbl_mw_datasignal_subscribe(data_signal, fcn_dptr)

time.sleep(10.0)

# Unsubscribe:
libmetawear.mbl_mw_datasignal_unsubscribe(data_signal)

time.sleep(1.0)

c.disconnect()

