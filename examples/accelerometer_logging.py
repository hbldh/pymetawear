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
from pymetawear.exceptions import PyMetaWearException, PyMetaWearDownloadTimeout

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

time.sleep(1.0)
print("\n")

client.accelerometer.high_frequency_stream = False

client.accelerometer.start_logging()
print("Logging accelerometer data...")

time.sleep(0.25)

client.accelerometer.stop_logging()
print("Logging stopped.")

print("\nDownloading data...")
download_done = False
n = 0
data = None
while download_done and n < 3:
    try:
        data = client.accelerometer.download_log(timeout=10.0)
        download_done = True
    except PyMetaWearDownloadTimeout:
        print("Download of log interrupted. Trying to reconnect...")
        client.disconnect()
        client.connect()
        n += 1
if data is None:
    raise PyMetaWearException("Download of logging data failed.")

for d in data:
    print(d)

pattern = client.led.load_preset_pattern('blink', repeat_count=10)
client.led.write_pattern(pattern, 'g')
client.led.play()

time.sleep(5.0)

client.led.stop_and_clear()

print("\nDisconnecting...")
client.disconnect()
