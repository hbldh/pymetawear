#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:mod:`accelerometer`
==================

Updated by lkasso <hello@mbientlab.com>
Created by hbldh <henrik.blidh@nedomkull.com>
Created on 2016-04-10

"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import time

from pymetawear.discover import select_device
from pymetawear.client import MetaWearClient

address = select_device()
c = MetaWearClient(str(address), debug=True)
print("New client created: {0}".format(c))

print("Get possible accelerometer settings...")
settings = c.accelerometer.get_possible_settings()
print(settings)

time.sleep(1.0)

print("Write accelerometer settings...")
c.accelerometer.set_settings(data_rate=3.125, data_range=4.0)

time.sleep(1.0)

print("Check accelerometer settings...")
settings = c.accelerometer.get_current_settings()
print(settings)

print("Subscribing to accelerometer signal notifications...")
c.accelerometer.high_frequency_stream = False
c.accelerometer.notifications(lambda data: print(data))

time.sleep(10.0)

print("Unsubscribe to notification...")
c.accelerometer.notifications(None)

time.sleep(5.0)

c.disconnect()
