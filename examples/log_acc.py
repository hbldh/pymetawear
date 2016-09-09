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
import copy
from ctypes import cast, POINTER, c_float, c_long, byref, c_uint8

from discover import scan_and_select_le_device
from pymetawear.client import MetaWearClient, libmetawear
from pymetawear.mbientlab.metawear.core import \
    CartesianFloat, DataTypeId, FnDataPtr, FnUintUint, \
    LogDownloadHandler, FnVoid, FnUbyteUlongByteArray

address = scan_and_select_le_device()
c = MetaWearClient(str(address), 'pybluez', debug=False)
print("New client created: {0}".format(c))

print("Write accelerometer settings...")
c.accelerometer.set_settings(data_rate=50.0, data_range=8.0)

output = []


def acc_callback(data):
    """Handle a (x,y,z) accelerometer tuple."""
    output.append(data)


def acc_data_progress_update_handler(entries_left, total_entries):
    print("Entries {0} / {1}".format(entries_left, total_entries))


def cartesian_float_data_handler(data):
    epoch = data.contents.epoch
    contents = copy.deepcopy(cast(data.contents.value, POINTER(CartesianFloat)).contents)
    output.append((epoch, (contents.x, contents.y, contents.z)))
    #print("[{0}] {1}".format(epoch, (contents.x, contents.y, contents.z)))


progress_update = FnUintUint(acc_data_progress_update_handler)
download_handler = LogDownloadHandler(
    received_progress_update=progress_update,
    received_unknown_entry=cast(None, FnUbyteUlongByteArray))


def logger_ready_handler():
    libmetawear.mbl_mw_logging_download(c.board, c_uint8(10), byref(download_handler))
    #for buffer in Bmi160Accelerometer.log_responses:
    #    self.libmetawear.mbl_mw_connection_notify_char_changed(self.board, buffer.raw, len(buffer.raw))

cartesian_float_data = FnDataPtr(cartesian_float_data_handler)
logger_ready = FnVoid(logger_ready_handler)


print("Clear old log entries...")
#libmetawear.mbl_mw_logging_clear_entries(c.board)
time.sleep(1.0)

print("Start logging...")
libmetawear.mbl_mw_logging_start(c.board, 0)
time.sleep(1.0)
print("Activate logging for acc...")
libmetawear.mbl_mw_datasignal_log(c.accelerometer.data_signal, cartesian_float_data, logger_ready)
time.sleep(1.0)

print("Start accelerometers...")
c.accelerometer.toggle_sampling(True)
c.accelerometer.start()
c.accelerometer.notifications(acc_callback)
time.sleep(1.0)





time.sleep(20.0)

libmetawear.mbl_mw_datasignal_remove_logger(c.accelerometer.data_signal)
c.accelerometer.stop()
c.accelerometer.toggle_sampling(False)
libmetawear.mbl_mw_logging_stop(c.board)

time.sleep(5.0)

c.disconnect()

import matplotlib.pyplot as plt
import numpy as np

dt = np.array([float(d[0]) for d in output])
dt -= dt[0]
dt /= 1000.
acc = np.array([np.array(d[1], 'float') for d in output])

plt.plot(dt, acc[:, 0], 'b')
plt.plot(dt, acc[:, 1], 'g')
plt.plot(dt, acc[:, 2], 'r')

plt.show()


