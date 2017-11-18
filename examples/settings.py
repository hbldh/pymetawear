#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:mod:`accelerometer`
==================

Updated by lkasso <hello@mbientlab.com>
Created by hbldh <henrik.blidh@nedomkull.com>
Created on 2016-04-10

"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import time
from ctypes import c_ubyte, POINTER, cast, create_string_buffer

from pymetawear.discover import select_device
from pymetawear.client import MetaWearClient

address = select_device()
c = MetaWearClient(str(address), debug=True)
print("New client created: {0}".format(c))


#print("Set connection parameters...")
#c.settings.set_connection_parameters(min_conn_interval=750, max_conn_interval=1000, latency=128, timeout=16384)

#time.sleep(2.0)

print("Set new device name...")
c.settings.set_device_name(name="Antiware")

time.sleep(2.0)

print("Set Tx power to -20...")
c.settings.set_tx_power(power=-20)

time.sleep(2.0)

scan_response= "\x03\x03\xD8\xfe\x10\x16\xd8\xfe\x00\x12\x00\x6d\x62\x69\x65\x6e\x74\x6c\x61\x62\x00"
print("Set custom scan response...")
c.settings.set_scan_response(response=scan_response)

time.sleep(2.0)

print("Set advertising parameters...")
c.settings.set_ad_interval(interval=417, timeout=0)

time.sleep(2.0)

print("Start advertising...")
c.settings.start_advertising()

#this is a good time to call hcidump and verify changes
time.sleep(1.0)

c.disconnect()
