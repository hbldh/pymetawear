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
c = MetaWearClient(str(address), 'pygatt', debug=True)
print("New client created: {0}".format(c))


def acc_callback(data):
    """Handle a (epoch, (x,y,z)) accelerometer tuple."""
    print("Epoch time: [{0}] - X: {1}, Y: {2}, Z: {3}".format(data[0], *data[1]))


print("Write accelerometer settings...")
c.accelerometer.set_settings(data_rate=100.0, data_range=4.0)
print("Subscribing to accelerometer signal notifications...")
c.accelerometer.high_frequency_stream = False
c.accelerometer.notifications(acc_callback)

time.sleep(20.0)

print("Unsubscribe to notification...")
c.accelerometer.notifications(None)

time.sleep(5.0)

c.disconnect()
