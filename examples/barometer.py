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

from discover import scan_and_select_le_device
from pymetawear.client import MetaWearClient

address = scan_and_select_le_device()
c = MetaWearClient(str(address), 'pybluez', debug=True)
print("New client created: {0}".format(c))


def baro_callback(data):
    """Handle a (epoch, value) barometer tuple."""
    print("Epoch time: [{0}] - Altitude: {1}".format(data[0], data[1]))


print("Write barometer settings...")
c.barometer.set_settings(oversampling='high',
                         iir_filter='avg_8',
                         standby_time=250.0)
print("Subscribing to barometer signal notifications...")
c.barometer.notifications(baro_callback)

time.sleep(20.0)

print("Unsubscribe to notification...")
c.barometer.notifications(None)

time.sleep(5.0)

c.disconnect()
