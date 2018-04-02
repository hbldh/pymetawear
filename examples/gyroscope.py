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
from __future__ import absolute_import

import time

from pymetawear.discover import select_device
from pymetawear.client import MetaWearClient

address = select_device()
c = MetaWearClient(str(address), debug=True)
print("New client created: {0}".format(c))


print("Write gyroscope settings...")
settings = c.gyroscope.get_possible_settings()
print(settings)

time.sleep(5.0)

print("Write gyroscope settings...")
c.gyroscope.set_settings(data_rate=50.0, data_range=1000.0)

time.sleep(5.0)

print("Subscribing to gyroscope signal notifications...")
c.gyroscope.notifications(lambda data: print(data))

time.sleep(20.0)

print("Unsubscribe to notification...")
c.gyroscope.notifications(None)

time.sleep(5.0)

c.disconnect()
