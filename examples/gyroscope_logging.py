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

print("Get possible gyroscope settings of client 1...")
settings = client.gyroscope.get_possible_settings()
print(settings)

time.sleep(1.0)

print("\nWrite gyroscope settings...")
client.gyroscope.set_settings(data_rate=400, data_range=1000.0)

time.sleep(1.0)

print("\nCheck gyroscope settings of client 1...")
settings = client.gyroscope.get_current_settings()
print(settings)

time.sleep(1.0)
print("\n")

client.gyroscope.high_frequency_stream = False

client.gyroscope.start_logging()
print("Logging gyroscope data...")

time.sleep(0.25)

client.gyroscope.stop_logging()
print("Logging stopped.")

print("\nDownloading data...")
data = client.gyroscope.download_log()
for d in data:
    print(d)

pattern = client.led.load_preset_pattern('blink', repeat_count=10)
client.led.write_pattern(pattern, 'g')
client.led.play()

time.sleep(5.0)

client.led.stop_and_clear()

print("\nDisconnecting...")
client.disconnect()
