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
from pymetawear.exceptions import PyMetaWearException
from pymetawear.mbientlab.metawear.core import CartesianFloat, DataTypeId, FnDataPtr

from ..discover import scan_and_select_le_device
from pymetawear.client import MetaWearClient

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
_acc_callback = FnDataPtr(acc_callback)


print("Write accelerometer settings...")
libmetawear.mbl_mw_acc_set_odr(c.board, c_float(200.0))
libmetawear.mbl_mw_acc_set_range(c.board, c_float(2.0))
print("Write accelerometer config....")
libmetawear.mbl_mw_acc_write_acceleration_config(c.board)
print("Subscribing to accelerometer signal...")
libmetawear.mbl_mw_acc_get_acceleration_data_signal.restype = c_long
data_signal = c_long(libmetawear.mbl_mw_acc_get_acceleration_data_signal(c.board))
libmetawear.mbl_mw_datasignal_subscribe(data_signal, _acc_callback)
print("Enable acc sampling on board...")
libmetawear.mbl_mw_acc_enable_acceleration_sampling(c.board)
print("Start acc on board...")
libmetawear.mbl_mw_acc_start(c.board)

time.sleep(20.0)

print("Unsubscribe to notification...")
libmetawear.mbl_mw_datasignal_unsubscribe(data_signal)
print("Stop accelerometer...")
libmetawear.mbl_mw_acc_stop(c.board)
print("Disable accelerometer sampling...")
libmetawear.mbl_mw_acc_disable_acceleration_sampling(c.board)

time.sleep(5.0)

c.disconnect()
