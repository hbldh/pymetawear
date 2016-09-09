#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:mod:`gyroscope`
==================

Created by hbldh <henrik.blidh@nedomkull.com>
Created on 2016-04-26

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


def gyro_callback(data):
    """Handle a (epoch, (x,y,z)) gyroscope tuple."""
    print("Epoch time: [{0}] - X: {1}, Y: {2}, Z: {3}".format(data[0], *data[1]))


print("Write gyroscope settings...")
c.gyroscope.set_settings(data_rate=200.0, data_range=1000.0)
print("Subscribing to gyroscope signal notifications...")
c.gyroscope.notifications(gyro_callback)

time.sleep(20.0)

print("Unsubscribe to notification...")
c.gyroscope.notifications(None)

time.sleep(5.0)

c.disconnect()
