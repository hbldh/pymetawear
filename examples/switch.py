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

import time

from pymetawear.discover import select_device
from pymetawear.client import MetaWearClient

address = select_device()
c = MetaWearClient(str(address), debug=True)
print("New client created: {0}".format(c))

# Create subscription
c.switch.notifications(lambda data: print(data))

time.sleep(10.0)

# Remove subscription
c.switch.notifications(None)
time.sleep(1.0)

c.disconnect()
