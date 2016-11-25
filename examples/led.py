#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:mod:`led`
==================

Created by hbldh <henrik.blidh@nedomkull.com>
Created on 2016-04-02

"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import time

from pymetawear.discover import select_device
from pymetawear.client import MetaWearClient

address = select_device()
c = MetaWearClient(str(address), 'pygatt', debug=True)
print("New client created: {0}".format(c))

print("Blinking 10 times with green LED...")
pattern = c.led.load_preset_pattern('blink', repeat_count=10)
c.led.write_pattern(pattern, 'g')
c.led.play()

time.sleep(5.0)

c.disconnect()
