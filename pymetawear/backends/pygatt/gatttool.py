#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:mod:`gatttool`
==================

Created by hbldh <henrik.blidh@nedomkull.com>
Created on 2016-04-02

"""

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import

import re

import pygatt


class PyMetaWearGATTToolBackend(pygatt.backends.GATTToolBackend):
    """Minor modification of the GATTToolBackend to handle multiple byte output from notifications.

    Will be removed if pull request is accepted.

    """

    def __init__(self, *args, **kwargs):
        self._notification_regex = re.compile("=\s(0x[0-9a-fA-F]{4})\svalue:\s(.*)$")
        super(PyMetaWearGATTToolBackend, self).__init__(*args, **kwargs)

    def _handle_notification_string(self, msg):
        hex_handle, hex_values = self._notification_regex.search(msg.strip()).groups()
        handle = int(hex_handle, 16)
        value = bytearray([int(x, 16) for x in hex_values.strip().split(' ')])
        if self._connected_device is not None:
            self._connected_device.receive_notification(handle, value)
