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
import threading
import uuid
import warnings
from ctypes import create_string_buffer

from bluepy.btle import Peripheral, ADDR_TYPE_RANDOM, BTLEException, DefaultDelegate, Characteristic

from pymetawear.exceptions import PyMetaWearException, PyMetaWearConnectionTimeout
from pymetawear.utils import range_, string_types, bytearray_to_str
from pymetawear.backends import BLECommunicationBackend

__all__ = ["BluepyBackend"]


class BluepyDelegate(DefaultDelegate):

    def __init__(self, notify_fcn, *args, **kwargs):
        DefaultDelegate.__init__(self)
        self.notify_fcn = notify_fcn

    def handleNotification(self, cHandle, data):
        self.notify_fcn(cHandle, data)


class BluepyBackend(BLECommunicationBackend):
    """
    Backend using `bluepy <https://github.com/IanHarvey/bluepy>`_
    for BLE communication.
    """

    def __init__(self, address, interface=None, async=False, timeout=None, debug=False):
        self._primary_services = {}
        self._characteristics_cache = {}
        self._peripheral = None

        warnings.warn("Bluepy backend does not handle notifications properly yet.", RuntimeWarning)

        super(BluepyBackend, self).__init__(
            address, interface, async, 10.0 if timeout is None else timeout, debug)

    def _build_handle_dict(self):
        self._primary_services = {
            uuid.UUID(str(x.uuid)): (x.hndStart, x.hndEnd)
                for x in self.requester.getServices()}
        self._characteristics_cache = {
            uuid.UUID(str(x.uuid)): (x.valHandle, x.properties, x.valHandle + 1)
                for x in self.requester.getCharacteristics()}

    @property
    def _is_connected(self):
        try:
            status = self._peripheral.status().get('state') is not None
        except BTLEException:
            status = False
        except Exception:
            status = False
        return status

    @property
    def initialized(self):
        #self.requester.waitForNotifications(0.1)
        return self._initialization_status

    @property
    def requester(self):
        """Property handling `Peripheral` and its connection.

        :return: The connected GattRequester instance.
        :rtype: :class:`bluepy.btle.Peripheral`

        """

        if self._peripheral is None:
            if self._debug:
                print("Creating new Peripheral...")
            self._peripheral = Peripheral()

        if not self._is_connected:
            if self._debug:
                print("Connecting Peripheral...")
            self._peripheral.connect(
                self._address, addrType=ADDR_TYPE_RANDOM,
                iface=str(self._interface).replace('hci', ''))

            if not self._is_connected:
                raise PyMetaWearConnectionTimeout(
                    "Could not establish a connection to {0}.".format(self._address))

        return self._peripheral

    def disconnect(self):
        """Disconnect."""
        if self._peripheral is not None and self._is_connected:
            self._peripheral.disconnect()
            self._peripheral = None

    def _subscribe(self, characteristic_uuid, callback):
        # Subscribe to Notify Characteristic.
        handles = self._characteristics_cache.get(characteristic_uuid)
        c = Characteristic(self._peripheral, characteristic_uuid, *handles)
        bytes_to_send = str(bytearray([0x01, 0x00]))
        response = c.write(bytes_to_send, withResponse=True)
        self.requester.setDelegate(BluepyDelegate(callback))
        return response

    def _subscription_loop(self):

        while True:
            try:
                print("Waiting for notification")
                self.requester.waitForNotifications(1.0)
            except BTLEException as e:
                print("Error waiting: {0}".format(e))
                pass

    # Read and Write methods

    def read_gatt_char_by_uuid(self, characteristic_uuid):
        """Read the desired data from the MetaWear board
        using bluepy backend.

        :param uuid.UUID characteristic_uuid: Characteristic UUID to read from.
        :return: The read data.
        :rtype: str

        """
        handle = self.get_handle(characteristic_uuid)
        return self.requester.readCharacteristic(handle)

    def write_gatt_char_by_uuid(self, characteristic_uuid, data_to_send):
        """Write the desired data to the MetaWear board
        using bluepy backend.

        :param uuid.UUID characteristic_uuid: Characteristic UUID to write to.
        :param str data_to_send: Data to send.

        """
        handle = self.get_handle(characteristic_uuid)
        if not isinstance(data_to_send, string_types):
            data_to_send = data_to_send.decode('latin1')
        self.requester.writeCharacteristic(handle, data_to_send)

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

    def sleep(self, t):
        self.requester.waitForNotifications(t)
