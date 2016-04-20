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
import subprocess
from uuid import UUID

import pygatt
from pygatt import exceptions
from pygatt.backends.gatttool.gatttool import DEFAULT_CONNECT_TIMEOUT_S, log, \
    NotConnectedError, NotificationTimeout, GATTToolBLEDevice, pexpect

from pymetawear.utils import string_types


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
    """PyMetaWear overriding some method to handle some issues with pygatt.

    * Modification of the GATTToolBackend to handle multiple byte output from notifications.
    * Added BlueZ 4.X handling in ``connect``.

    Will be removed once pull request is drafted and accepted.

    """

    def __init__(self, *args, **kwargs):
        self._notification_regex = re.compile("=\s(0x[0-9a-fA-F]{4})\svalue:\s(.*)$")
        super(PyMetaWearGATTToolBackend, self).__init__(*args, **kwargs)

    def connect(self, address, timeout=DEFAULT_CONNECT_TIMEOUT_S,
                address_type='public'):
        log.info('Connecting with timeout=%s', timeout)
        self._con.sendline('sec-level low')
        self._address = address
        try:
            with self._connection_lock:
                cmd = 'connect %s %s' % (self._address, address_type)
                self._con.sendline(cmd)
                self._con.expect(
                    [b'Connection successful.*\[LE\]>',
                     self._address.encode().join([b'\[CON\]\[', b'\]\[LE\]'])],
                    timeout)
        except pexpect.TIMEOUT:
            message = ("Timed out connecting to %s after %s seconds."
                       % (self._address, timeout))
            log.error(message)
            raise NotConnectedError(message)

        self._connected_device = PyMetaWearGATTToolBLEDevice(address, self)
        return self._connected_device

    def _handle_notification_string(self, msg):
        hex_handle, hex_values = self._notification_regex.search(msg.decode().strip()).groups()
        handle = int(hex_handle, 16)
        value = bytearray([int(x, 16) for x in hex_values.strip().split(' ')])
        if self._connected_device is not None:
            self._connected_device.receive_notification(handle, value)
