#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
PyBlueZ backend
---------------

.. moduleauthor:: hbldh <henrik.blidh@nedomkull.com>
Created on 2016-04-02

"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import time
import uuid
from ctypes import create_string_buffer
import logging

try:
    from bluetooth.ble import GATTRequester, GATTResponse
    _import_failure = None
except ImportError as e:
    GATTRequester = object
    _import_failure = e

from pymetawear.exceptions import PyMetaWearException, PyMetaWearConnectionTimeout
from pymetawear.compat import range_, string_types, bytearray_to_str
from pymetawear.backends import BLECommunicationBackend

__all__ = ["PyBluezBackend"]

log = logging.getLogger(__name__)


class Requester(GATTRequester):

    def __init__(self, notify_fcn, *args):
        super(Requester, self).__init__(*args)
        self.notify_fcn = notify_fcn

    def on_notification(self, handle, data):
        return self.notify_fcn(handle, data[3:])


class PyBluezBackend(BLECommunicationBackend):
    """
    Backend using `pybluez <https://github.com/karulis/pybluez>`_ and
    `gattlib <https://bitbucket.org/OscarAcena/pygattlib>`_ for BLE communication.
    """

    def __init__(self, address, interface=None, timeout=None, debug=False):
        if _import_failure is not None:
            raise PyMetaWearException(
                "pybluez[ble] package error: {0}".format(_import_failure))
        self.name = 'pybluez/gattlib'
        self._primary_services = {}
        self._characteristics_cache = {}
        self._response = GATTResponse()
        if debug:
            log.setLevel(logging.DEBUG)

        super(PyBluezBackend, self).__init__(
            address, interface, 10.0 if timeout is None else timeout, debug)

    def _build_handle_dict(self):
        self._primary_services = {uuid.UUID(x.get('uuid')): (x.get('start'), x.get('end'))
                                  for x in self.requester.discover_primary()}
        self._characteristics_cache = {uuid.UUID(x.get('uuid')): (x.get('value_handle'), x.get('value_handle') + 1)
                                       for x in self.requester.discover_characteristics()}

    @property
    def is_connected(self):
        if self._requester is not None:
            return self._requester.is_connected()
        return False

    @property
    def requester(self):
        """Property handling `GattRequester` and its connection.

        :return: The connected GattRequester instance.
        :rtype: :class:`bluetooth.ble.GATTRequester`

        """
        if self._requester is None:
            self.connect()

        if not self.is_connected:
            raise PyMetaWearConnectionTimeout(
                "PyBluezBackend: Connection to {0} lost...".format(self._address))

        return self._requester

    def connect(self, clean_connect=False):
        if self.is_connected:
            return

        if clean_connect or self._requester is None:
            log.info("PyBluezBackend: Creating new GATTRequester...")
            self._requester = Requester(self.handle_notify_char_output,
                                        self._address,
                                        False, self._interface)

        log.info("PyBluezBackend: Connecting GATTRequester...")
        self._requester.connect(wait=False, channel_type='random')
        # Using manual waiting since gattlib's `wait` keyword does not work.
        t = 0.0
        t_step = 0.25
        while not self._requester.is_connected() and t < self._timeout:
            t += t_step
            time.sleep(t_step)

        if not self._requester.is_connected():
            raise PyMetaWearConnectionTimeout(
                "PyBluezBackend: Could not establish a connection to {0}.".format(self._address))

        super(PyBluezBackend, self).connect()

    def disconnect(self):
        """Disconnect."""
        if self._requester is not None and self._requester.is_connected():
            self._requester.disconnect()
            self._requester = None

    def _subscribe(self, characteristic_uuid, callback):
        # Subscribe to Notify Characteristic.
        handle = self.get_handle(characteristic_uuid, notify_handle=True)
        bytes_to_send = bytearray([0x01, 0x00])
        return self.requester.write_by_handle_async(
            handle, bytes(bytes_to_send), self._response)

    # Read and Write methods

    def read_gatt_char_by_uuid(self, characteristic):
        """Read the desired data from the MetaWear board
        using pybluez/gattlib backend.

        :param uuid.UUID characteristic_uuid: Characteristic UUID to read from.
        :return: The read data.
        :rtype: str

        """
        characteristic_uuid = self.get_uuid(characteristic)
        return self.requester.read_by_uuid(str(characteristic_uuid))[0]

    def write_gatt_char_by_uuid(self, characteristic, command, length):
        """Write the desired data to the MetaWear board
        using pybluez/gattlib backend.

        :param uuid.UUID characteristic_uuid: Characteristic UUID to write to.
        :param str data_to_send: Data to send.

        """
        characteristic_uuid = self.get_uuid(characteristic)
        handle = self.get_handle(characteristic_uuid)
        data_to_send = bytes(bytearray([command[i] for i in range_(length)]))
        if not isinstance(data_to_send, string_types):
            data_to_send = data_to_send.decode('latin1')
        self.requester.write_by_handle_async(handle, data_to_send, self._response)

    def get_handle(self, characteristic_uuid, notify_handle=False):
        """Get handle for a characteristic UUID.

        :param uuid.UUID characteristic_uuid: The UUID for the characteristic to look up.
        :param bool notify_handle:
        :return: The handle for this UUID.
        :rtype: int

        """
        if isinstance(characteristic_uuid, string_types):
            characteristic_uuid = characteristic_uuid.UUID(
                characteristic_uuid)
        handle = self._characteristics_cache.get(
            characteristic_uuid, [None, None])[int(notify_handle)]
        if handle is None:
            raise PyMetaWearException("Incorrect characteristic.")
        else:
            return handle

    def _response_2_string_buffer(self, response):
        return create_string_buffer(bytearray_to_str(response), len(response))
