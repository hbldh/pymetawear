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
from __future__ import absolute_import

import time
from ctypes import cast, POINTER

from pymetawear.client import MetaWearClient, libmetawear
from pymetawear.discover import select_device
from pymetawear.exceptions import PyMetaWearException
from pymetawear.mbientlab.metawear.core import \
    CartesianFloat, DataTypeId, Fn_DataPtr


address = select_device()
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
