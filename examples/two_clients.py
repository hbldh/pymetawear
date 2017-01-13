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
from pymetawear.client import MetaWearClient

address_1 = 'DD:3A:7D:4D:56:F0'
address_2 = 'FF:50:35:82:3B:5A'

print("Connect to {0}...".format(address_1))
client_1 = MetaWearClient(str(address_1), timeout=10.0, debug=False)
print("New client created: {0}".format(client_1))
print("Connect to {0}...".format(address_2))
client_2 = MetaWearClient(str(address_2), timeout=10.0, debug=False)
print("New client created: {0}".format(client_2))

print("Blinking 10 times with green LED on client 1...")
pattern = client_1.led.load_preset_pattern('blink', repeat_count=10)
client_1.led.write_pattern(pattern, 'g')
client_1.led.play()

print("Blinking 10 times with red LED on client 2...")
pattern = client_2.led.load_preset_pattern('blink', repeat_count=10)
client_2.led.write_pattern(pattern, 'r')
client_2.led.play()

time.sleep(5.0)

client_1.disconnect()
client_2.disconnect()
