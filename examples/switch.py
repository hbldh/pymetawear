#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:mod:`led`
==================

Created by hbldh <henrik.blidh@nedomkull.com>
Created on 2016-04-02

"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import time

from discover import scan_and_select_le_device
from pymetawear.client import MetaWearClient

address = scan_and_select_le_device()
c = MetaWearClient(str(address), 'pybluez', debug=True)
print("New client created: {0}".format(c))


def switch_callback(data):
    """Handle a (epoch, status) switch tuple."""
    epoch = data[0]
    status = data[1]
    print("[{0}] Switch {1}!".format(
        epoch, 'pressed' if status else 'released'))


# Create subscription
c.switch.notifications(switch_callback)

time.sleep(10.0)

# Remove subscription
c.switch.notifications(None)
time.sleep(1.0)

c.disconnect()
