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

from ctypes import POINTER, c_float, cast
import time

from pymetawear import libmetawear
from pymetawear.client import MetaWearClient
from pymetawear.discover import select_device
from pymetawear.mbientlab.metawear.core import DataTypeId, Fn_DataPtr

address = select_device()
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
data_signal = libmetawear.mbl_mw_multi_chnl_temp_get_temperature_data_signal(c.board, channel)
fcn_dptr = Fn_DataPtr(temperature_callback)
libmetawear.mbl_mw_datasignal_subscribe(data_signal, fcn_dptr)

for i in range(5):
    libmetawear.mbl_mw_datasignal_read(data_signal)
    time.sleep(1.0)

# Unsubscribe to notifications
libmetawear.mbl_mw_datasignal_unsubscribe(data_signal)

time.sleep(1.0)

c.disconnect()

