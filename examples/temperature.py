#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:mod:`battery`
==================

Created by hbldh <henrik.blidh@nedomkull.com>
Created on 2016-04-02

"""

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import

import time

from discover import scan_and_select_le_device
from pymetawear.client import MetaWearClient

address = scan_and_select_le_device()
c = MetaWearClient(str(address), 'pygatt', timeout=10, debug=False)
print("New client created: {0}".format(c))


def temperature_callback(data):
    epoch = data[0]
    temp = data[1]
    print("[{0}] Temperature {1} \u2103".format(epoch, temp))

for channel in c.temperature.channels:

    c.temperature.set_settings(channel)
    time.sleep(0.1)

    print("Subscribe to {0} Temperature notifications...".format(channel))
    c.temperature.notifications(temperature_callback)
    time.sleep(1.0)

    print("Trigger {0} temperature notification...".format(channel))
    c.temperature.read_temperature()
    time.sleep(1.0)

    print("Unsubscribe to temperature notifications...")
    c.temperature.notifications(None)
    time.sleep(1.0)

c.disconnect()
