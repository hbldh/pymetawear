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
c = MetaWearClient(str(address), 'pygatt', debug=True)
print("New client created: {0}".format(c))


def battery_callback(data):
    """Handle a battery status tuple."""
    epoch = data[0]
    battery = data[1]
    print("[{0}] Voltage: {1}, Charge: {2}".format(
        epoch, battery[0], battery[1]))


print("Subscribe to battery notifications...")
c.battery.notifications(battery_callback)
time.sleep(1.0)

print("Trigger battery state notification...")
c.battery.read_battery_state()
time.sleep(1.0)

print("Unsubscribe to battery notifications...")
c.battery.notifications(None)
time.sleep(1.0)

c.disconnect()
