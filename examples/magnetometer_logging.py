#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:mod:'magnetometer_logging.py'
==================
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

client = MetaWearClient(str(address), debug=False)
print("New client created: {0}".format(client))

settings = client.magnetometer.get_possible_settings()
print("Possible magnetometer settings of client:")
for k, v in settings.items():
    print(k, v)

print("Write magnetometer settings...")
c.magnetometer.set_settings(power_preset='REGULAR')

settings = client.magnetometer.get_current_settings()
print("Magnetometer settings of client: {0}".format(settings))

time.sleep(0.2)

client.magnetometer.high_frequency_stream = False
client.magnetometer.start_logging()
print("Logging magnetometer data...")

time.sleep(3.0)

client.magnetometer.stop_logging()
print("Logging stopped.")

print("Downloading data...")
data = client.magnetometer.download_log()
for d in data:
    print(d)

print("Disconnecting...")
client.disconnect()
