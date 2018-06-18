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

client = MetaWearClient(str(address), debug=False)
print("New client created: {0}".format(client))

settings = client.accelerometer.get_possible_settings()
print("Possible accelerometer settings of client:")
for k, v in settings.items():
    print(k, v)

print("Write accelerometer settings...")
client.accelerometer.set_settings(data_rate=400, data_range=4.0)

settings = client.accelerometer.get_current_settings()
print("Accelerometer settings of client: {0}".format(settings))

client.accelerometer.high_frequency_stream = False
client.accelerometer.start_logging()
print("Logging accelerometer data...")

time.sleep(10.0)

client.accelerometer.stop_logging()
print("Logging stopped.")

print("Downloading data...")
download_done = False
n = 0
data = None
while (not download_done) and n < 3:
    try:
        data = client.accelerometer.download_log()
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

print("Disconnecting...")
client.disconnect()
