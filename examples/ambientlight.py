#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:mod:`gyroscope`
==================

Updated by lkasso <hello@mbientlab.com>
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

if c.ambient_light.is_present:
    print("Get ambient light settings...")
    settings = c.ambient_light.get_possible_settings()
    print(settings)

    time.sleep(1.0)

    print("Write ambient light settings...")
    c.ambient_light.set_settings(gain=4, integration_time=200, measurement_rate=200)

    time.sleep(1.0)
    
    print("Subscribing to ambient light signal notifications...")
    c.ambient_light.notifications(lambda data: print(data))

    time.sleep(20.0)

    print("Unsubscribe to notification...")
    c.ambient_light.notifications(None)

    time.sleep(5.0)

else:
    print("Ambient light sensor is not present on this board.")

c.disconnect()
