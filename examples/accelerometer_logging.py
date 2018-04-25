#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:mod:'accelerometer_logging.py'
==================
Updated by dmatthes1982 <dmatthes@cbs.mpg.de>
Created by hbldh <henrik.blidh@nedomkull.com>
Created on 2018-04-20
"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import time

from pymetawear.discover import select_device
from pymetawear.client import MetaWearClient

address = select_device()

client = MetaWearClient(str(address), debug=True)
print("New client created: {0}".format(client))

print("Get possible accelerometer settings of client 1...")
settings = client.accelerometer.get_possible_settings()
print(settings)

time.sleep(1.0)

print("\nWrite accelerometer settings...")
client.accelerometer.set_settings(data_rate=400, data_range=4.0)

time.sleep(1.0)

print("\nCheck accelerometer settings of client 1...")
settings = client.accelerometer.get_current_settings()
print(settings)

client.accelerometer.high_frequency_stream = False
client.accelerometer.logging = True

client.accelerometer.start_logging()
print("\nLogging...")

time.sleep(0.5)
print("Logging stopped.")

client.accelerometer.download_log(lambda data : print(data))
print("\nDownloading Data...")

time.sleep(5.0)

print("\nDisconnecting...")
client.disconnect()
