#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:mod:`pygattlib`
==================

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

from gattlib import GATTRequester

from pymetawear.client import MetaWearClient, libmetawear
from pymetawear.exceptions import PyMetaWearConnectionTimeout, PyMetaWearException
from pymetawear.specs import METAWEAR_SERVICE_NOTIFY_CHAR

__all__ = ["MetaWearClientPyGattLib"]


class MetaWearClientPyGattLib(MetaWearClient):
    """
    Client using `pygattlib <https://bitbucket.org/OscarAcena/pygattlib>`_
    for BLE communication.
    """

    def __init__(self, address, debug=False):

        self._address = address
        self._debug = debug
        self._requester = None

        self._build_service_and_characterstics_cache()

        # Subscribe to Notify Characteristic.
        self.requester.write_by_handle(
            self.get_handle(METAWEAR_SERVICE_NOTIFY_CHAR[1], notify_handle=True),
            bytes(bytearray([0x01, 0x00])))

        super(MetaWearClientPyGattLib, self).__init__(address, debug)

    @property
    def requester(self):
        """Property handling `GattRequester` and its connection.

        :return: The connected GattRequester instance.
        :rtype: :class:`bluetooth.ble.GATTRequester`

        """
        if self._requester is None:
            if self._debug:
                print("Creating new GATTRequester...")
            self._requester = Requester(self._handle_notification, self._address, False)

        if not self._requester.is_connected():
            if self._debug:
                print("Connecting GATTRequester...")
            self._requester.connect(wait=False, channel_type='random')
            # Using manual waiting since gattlib's `wait` keyword does not work.
            t = 0.0
            while not self._requester.is_connected() and t < 5.0:
                t += 0.1
                time.sleep(0.1)

            if not self._requester.is_connected():
                raise PyMetaWearConnectionTimeout("Could not establish a connection to {0}.".format(self._address))

        return self._requester

    # Callback methods

    def _handle_notification(self, handle, value):
        #print(type(value))
        #print(len(value))
        #print("data received: {0}".format(value))
        #print("bytes received: {0}".format(" ".join([hex(ord(b)) for b in value])))
        if handle == self.get_handle(METAWEAR_SERVICE_NOTIFY_CHAR[1], notify_handle=False):
            print("- notification on handle {0}: {1}\n".format(handle, value))
            sb = create_string_buffer(bytes(value), len(bytes(value)))
            print(sb.raw)
            libmetawear.mbl_mw_connection_notify_char_changed(self.board, sb.raw, len(sb.raw))
        else:
            print("- notification on handle {0}: {1}\n".format(handle, value))

    def _read_gatt_char(self, characteristic):
        """Read the desired data from the MetaWear board.

        :param pymetawear.mbientlab.metawear.core.GattCharacteristic characteristic: :class:`ctypes.POINTER`
            to a GattCharacteristic.
        :return: The read data.
        :rtype: str

        """
        service_uuid, characteristic_uuid = self._characteristic_2_uuids(characteristic.contents)
        response = self.requester.read_by_uuid(str(characteristic_uuid))[0]

        if self._debug:
            print("data received: {0}".format(response))
            print("bytes received: {0}".format(" ".join([hex(ord(b)) for b in response])))

        sb = self._read_response_to_buffer(response)
        libmetawear.mbl_mw_connection_char_read(self.board, characteristic, sb.raw, len(sb.raw))

    def _write_gatt_char(self, characteristic, command, length):
        """Write the desired data to the MetaWear board.

        :param pymetawear.mbientlab.metawear.core.GattCharacteristic characteristic:
        :param POINTER command: The command to send, as a byte array pointer.
        :param int length: Length of the array that command points.
        :return:
        :rtype:

        """
        service_uuid, characteristic_uuid = self._characteristic_2_uuids(characteristic.contents)
        handle = self.get_handle(characteristic_uuid)
        data_to_send = self._command_to_str(command, length)
        self.requester.write_by_handle(handle, data_to_send)

    def _build_service_and_characterstics_cache(self):
        self._primary_services = {uuid.UUID(x.get('uuid')): (x.get('start'), x.get('end'))
                                  for x in self.requester.discover_primary()}
        self._characteristics_cache = {uuid.UUID(x.get('uuid')): (x.get('value_handle'), x.get('value_handle') + 1)
                                       for x in self.requester.discover_characteristics()}

    def get_handle(self, uuid, notify_handle=False):
        if isinstance(uuid, basestring):
            uuid = uuid.UUID(uuid)
        handle = self._characteristics_cache.get(uuid, [None, None])[int(notify_handle)]
        if handle is None:
            raise PyMetaWearException("Incorrect characterstic.")
        return handle

    @staticmethod
    def _command_to_str(command, length):
        return bytes(bytearray([command[i] for i in range_(length)]))

    @staticmethod
    def _read_response_to_buffer(response):
        return create_string_buffer(response.encode('utf8'), len(response))

    @staticmethod
    def _notify_response_to_buffer(response):
        return create_string_buffer(response.encode('utf8'), len(response))


class Requester(GATTRequester):

    def __init__(self, notify_fcn, *args):
        GATTRequester.__init__(self, *args)
        self.notify_fcn = notify_fcn

    def on_notification(self, handle, data):
        return self.notify_fcn(handle, data)
