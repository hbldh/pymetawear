#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:mod:'gyroscope_logging.py'
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

settings = client.gyroscope.get_possible_settings()
print("Possible gyroscope settings of client:")
for k, v in settings.items():
    print(k, v)

print("Write gyroscope settings...")
client.gyroscope.set_settings(data_rate=400, data_range=1000.0)

settings = client.gyroscope.get_current_settings()
print("Gyroscope settings of client: {0}".format(settings))

time.sleep(0.2)

client.gyroscope.high_frequency_stream = False
client.gyroscope.start_logging()
print("Logging gyroscope data...")

time.sleep(3.0)

client.gyroscope.stop_logging()
print("Logging stopped.")

print("Downloading data...")
data = client.gyroscope.download_log()
for d in data:
    print(d)

pattern = client.led.load_preset_pattern('blink', repeat_count=10)
client.led.write_pattern(pattern, 'g')
client.led.play()

time.sleep(5.0)

client.led.stop_and_clear()

print("Disconnecting...")
client.disconnect()
