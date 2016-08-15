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
from __future__ import unicode_literals
from __future__ import absolute_import

import time

from discover import scan_and_select_le_device
from pymetawear.client import MetaWearClient

address = scan_and_select_le_device()
c = MetaWearClient(str(address), 'pygatt', debug=True)
print("New client created: {0}".format(c))

if c.ambient_light.is_present:
    def callback(data):
        """Handle ambient light notification callback."""
        print("Ambient Light: {0}".format(data))


    print("Write ambient light settings...")
    c.ambient_light.set_settings(gain=4, integration_time=200, measurement_rate=200)
    print("Subscribing to ambient light signal notifications...")
    c.ambient_light.notifications(callback)

    time.sleep(20.0)

    print("Unsubscribe to notification...")
    c.ambient_light.notifications(None)

    time.sleep(5.0)
else:
    print("Ambient light sensor is not present on this board.")

c.disconnect()
