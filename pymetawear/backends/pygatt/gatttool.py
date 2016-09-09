#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""

Created by hbldh <henrik.blidh@nedomkull.com>
Created on 2016-04-02

"""

from __future__ import division
from __future__ import print_function
#from __future__ import unicode_literals
from __future__ import absolute_import

import re
from uuid import UUID

import pygatt
from pygatt import exceptions
from pygatt.backends.gatttool.gatttool import log, GATTToolBLEDevice, DEFAULT_CONNECT_TIMEOUT_S

from pymetawear.utils import string_types

if hasattr(bytes, 'fromhex'):
    # Python 3.
    def _hex_value_parser(x):
        return bytes.fromhex(x.decode('utf8'))
else:
    # Python 2.7
    def _hex_value_parser(x):
        return bytearray.fromhex(x)


class PyMetaWearGATTToolBLEDevice(GATTToolBLEDevice):
    """PyMetaWear overriding ``get_handle`` method
    to make it Python 3 compliant."""

    def get_handle(self, char_uuid):
        """
        Look up and return the handle for an attribute by its UUID.
        :param char_uuid: The UUID of the characteristic.
        :type uuid: str
        :return: None if the UUID was not found.
        """
        if isinstance(char_uuid, string_types):
            char_uuid = UUID(char_uuid)
        log.debug("Looking up handle for characteristic %s", char_uuid)
        if char_uuid not in self._characteristics:
            # TODO need to expose discovering characterstics via BLEDevice
            self._characteristics = self.discover_characteristics()

        characteristic = self._characteristics.get(char_uuid)
        if characteristic is None:
            message = "No characteristic found matching %s" % char_uuid
            log.warn(message)
            raise exceptions.BLEError(message)

        # TODO support filtering by descriptor UUID, or maybe return the whole
        # Characteristic object
        log.debug("Found %s" % characteristic)
        return characteristic.handle


class PyMetaWearGATTToolBackend(pygatt.backends.GATTToolBackend):
    """PyMetaWear overriding ``_handle_notification_string`` to
    address some issues with pygatt.

    Will be removed once pull request is drafted and accepted.

    """

    def __init__(self, *args, **kwargs):
        super(PyMetaWearGATTToolBackend, self).__init__(*args, **kwargs)

    def _handle_notification_string(self, event):
        msg = event["after"]
        if not msg:
            log.warn("Blank message received in notification, ignored")
            return

        split_msg = msg.strip().split(None, 5)
        if len(split_msg) < 6:
            log.warn("Unable to parse notification string, ignoring: %s", msg)
            return

        hex_handle, _, hex_values = split_msg[3:]
        handle = int(hex_handle, 16)
        value = _hex_value_parser(hex_values)
        if self._connected_device is not None:
            self._connected_device.receive_notification(handle, value)
