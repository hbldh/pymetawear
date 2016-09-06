#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""

.. moduleauthor:: hbldh <henrik.blidh@nedomkull.com>
Created on 2016-04-02

"""

from __future__ import division
from __future__ import print_function
#from __future__ import unicode_literals
from __future__ import absolute_import

import time
import uuid
from ctypes import create_string_buffer

from bluetooth.ble import GATTRequester, GATTResponse

from pymetawear.exceptions import PyMetaWearException, PyMetaWearConnectionTimeout
from pymetawear.utils import range_, string_types, bytearray_to_str
from pymetawear.backends import BLECommunicationBackend

__all__ = ["PyBluezBackend"]


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

    def __init__(self, address, interface=None, async=True, timeout=None, debug=False):
        self._primary_services = {}
        self._characteristics_cache = {}
        self._response = GATTResponse()

        super(PyBluezBackend, self).__init__(
            address, interface, async, 10.0 if timeout is None else timeout, debug)

    def _build_handle_dict(self):
        self._primary_services = {uuid.UUID(x.get('uuid')): (x.get('start'), x.get('end'))
                                  for x in self.requester.discover_primary()}
        self._characteristics_cache = {uuid.UUID(x.get('uuid')): (x.get('value_handle'), x.get('value_handle') + 1)
                                       for x in self.requester.discover_characteristics()}

    @property
    def requester(self):
        """Property handling `GattRequester` and its connection.

        :return: The connected GattRequester instance.
        :rtype: :class:`bluetooth.ble.GATTRequester`

        """

        if self._requester is None:
            if self._debug:
                print("Creating new GATTRequester...")
            self._requester = Requester(self.handle_notify_char_output, self._address,
                                        False, self._interface)

        if not self._requester.is_connected():
            if self._debug:
                print("Connecting GATTRequester...")
            self._requester.connect(wait=False, channel_type='random')
            # Using manual waiting since gattlib's `wait` keyword does not work.
            t = 0.0
            t_step = 0.25
            while not self._requester.is_connected() and t < self._timeout:
                t += t_step
                time.sleep(t_step)

            if not self._requester.is_connected():
                raise PyMetaWearConnectionTimeout(
                    "Could not establish a connection to {0}.".format(self._address))

        return self._requester

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

    def read_gatt_char_by_uuid(self, characteristic_uuid):
        """Read the desired data from the MetaWear board
        using pybluez/gattlib backend.

        :param uuid.UUID characteristic_uuid: Characteristic UUID to read from.
        :return: The read data.
        :rtype: str

        """
        return self.requester.read_by_uuid(str(characteristic_uuid))[0]

    def write_gatt_char_by_uuid(self, characteristic_uuid, data_to_send):
        """Write the desired data to the MetaWear board
        using pybluez/gattlib backend.

        :param uuid.UUID characteristic_uuid: Characteristic UUID to write to.
        :param str data_to_send: Data to send.

        """
        handle = self.get_handle(characteristic_uuid)
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

    @staticmethod
    def mbl_mw_command_to_input(command, length):
        return bytes(bytearray([command[i] for i in range_(length)]))

    @staticmethod
    def read_response_to_str(response):
        return create_string_buffer(bytearray_to_str(response), len(response))

    @staticmethod
    def notify_response_to_str(response):
        bs = bytearray_to_str(response)
        return create_string_buffer(bs, len(bs))
