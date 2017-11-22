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

print("Get possible barometer settings...")
settings = c.barometer.get_possible_settings()
print(settings)

time.sleep(1.0)

print("Write barometer settings...")
c.barometer.set_settings(oversampling='HIGH',
                         iir_filter='AVG_8',
                         standby_time=250.0)

time.sleep(1.0)

print("Get current barometer settings...")
settings = c.barometer.get_current_settings()
print(settings)

time.sleep(5.0)

print("Subscribing to barometer signal notifications...")
c.barometer.notifications(lambda data: print(data))

time.sleep(20.0)

print("Unsubscribe to notification...")
c.barometer.notifications(None)

time.sleep(5.0)

c.disconnect()
