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

address_1 = 'XX:XX:XX:XX:XX:XX'
address_2 = 'XX:XX:XX:XX:XX:XX'
client_1 = MetaWearClient(str(address_1), debug=True)
client_2 = MetaWearClient(str(address_2), debug=True)

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
