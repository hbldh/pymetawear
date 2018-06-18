#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:mod:`magnetometer`
==================

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


print("Get possible magnetometer settings...")
settings = c.magnetometer.get_possible_settings()
print(settings)

time.sleep(1.0)

print("Write magnetometer settings...")
c.magnetometer.set_settings(power_preset='REGULAR')

time.sleep(1.0)

print("Subscribing to magnetometer signal notifications...")
c.magnetometer.notifications(lambda data: print(data))

time.sleep(10.0)

print("Unsubscribe to notification...")
c.magnetometer.notifications(None)

time.sleep(5.0)

c.disconnect()
