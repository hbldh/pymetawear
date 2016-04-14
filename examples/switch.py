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

from ctypes import byref, POINTER, c_uint, cast
import time

from pymetawear.client import discover_devices, MetaWearClient
from pymetawear.mbientlab.metawear.core import DataTypeId, FnDataPtr


print("Discovering nearby MetaWear boards...")
metawear_devices = discover_devices(timeout=2)
if len(metawear_devices) < 1:
    raise ValueError("No MetaWear boards could be detected.")
else:
    address = metawear_devices[0][0]

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

# Create subscription
c.switch_notifications(switch_callback)
time.sleep(10.0)
# Remove subscription
c.switch_notifications(None)
time.sleep(10.0)
# Add it once again
c.switch_notifications(switch_callback)
time.sleep(10.0)
# Remove it once more.
c.switch_notifications(None)
time.sleep(1.0)

# The code using libmetawear library directly instead of convenience methods in MetaWearClient:
#
# Subscribe:
# data_signal = libmetawear.mbl_mw_switch_get_state_data_signal(c.board)
# fcn_dptr = FnDataPtr(switch_callback)
# libmetawear.mbl_mw_datasignal_subscribe(data_signal, fcn_dptr)
#
# Unsubscribe:
# libmetawear.mbl_mw_datasignal_unsubscribe(data_signal)

c.disconnect()

