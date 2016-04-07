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

from pymetawear.client import MetaWearClient, libmetawear, range_
from pymetawear.exceptions import PyMetaWearConnectionTimeout, PyMetaWearException
from pymetawear.specs import METAWEAR_SERVICE_NOTIFY_CHAR

try:
    from bluetooth.ble import GATTRequester
    __all__ = ["MetaWearClientGattLib"]
    _import_failure = False
except ImportError:
    __all__ = []
    GATTRequester = object
    _import_failure = True


class MetaWearClientGattLib(MetaWearClient):
    """
    Client using `gattlib <https://bitbucket.org/OscarAcena/pygattlib>`_ for BLE communication.
    """

    def __init__(self, address, debug=False):

        if _import_failure:
            raise PyMetaWearException(
                'GattLib client not available. Install gattlib first.')

        self._address = address
        self._debug = debug
        self._requester = None

        self._build_service_and_characterstics_cache()

        # Subscribe to Notify Characteristic.
        self.requester.write_by_handle(
            self.get_handle(METAWEAR_SERVICE_NOTIFY_CHAR[1], notify_handle=True),
            bytes(bytearray([0x01, 0x00])))

        super(MetaWearClientGattLib, self).__init__(address, debug)

    @property
    def requester(self):
        """Property handling `GattRequester` and its connection.

        :return: The connected GattRequester instance.
        :rtype: :class:`bluetooth.ble.GATTRequester`

        """
        if self._requester is None:
            if self._debug:
                print("Creating new GATTRequester...")
            self._requester = Requester(self._handle_notify_char_output, self._address, False)

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

    def _backend_disconnect(self):
        if self._requester is not None and self._requester.is_connected():
            self._requester.disconnect()
            self._requester = None

    # Callback methods

    def _handle_notify_char_output(self, handle, value):
        value = value[3:] if len(value) > 4 else value
        super(MetaWearClientGattLib, self)._handle_notify_char_output(handle, value)

    def _backend_read_gatt_char(self, characteristic_uuid):
        """Read the desired data from the MetaWear board using pygatt backend.

        :param pymetawear.mbientlab.metawear.core.GattCharacteristic characteristic: :class:`ctypes.POINTER`
            to a GattCharacteristic.
        :return: The read data.
        :rtype: str

        """
        return self.requester.read_by_uuid(str(characteristic_uuid))[0]

    def _backend_write_gatt_char(self, characteristic_uuid, data_to_send):
        """Write the desired data to the MetaWear board using pygatt backend.

        :param uuid.UUID characteristic_uuid: The UUID to the characteristic to write to.
        :param str data_to_send: Data to send.

        """
        handle = self.get_handle(characteristic_uuid)
        self.requester.write_by_handle(handle, data_to_send)

    def _build_service_and_characterstics_cache(self):
        self._primary_services = {uuid.UUID(x.get('uuid')): (x.get('start'), x.get('end'))
                                  for x in self.requester.discover_primary()}
        self._characteristics_cache = {uuid.UUID(x.get('uuid')): (x.get('value_handle'), x.get('value_handle') + 1)
                                       for x in self.requester.discover_characteristics()}

    def get_handle(self, uuid, notify_handle=False):
        """Get handle for a characteristic.

        :param uuid.UUID uuid: The UUID for the characteristic to look up.
        :param bool notify_handle:
        :return: The handle for this UUID.
        :rtype: int

        """
        if isinstance(uuid, basestring):
            uuid = uuid.UUID(uuid)
        handle = self._characteristics_cache.get(uuid, [None, None])[int(notify_handle)]
        if handle is None:
            raise PyMetaWearException("Incorrect characterstic.")
        else:
            return handle

    @staticmethod
    def _mbl_mw_command_to_backend_input(command, length):
        return bytes(bytearray([command[i] for i in range_(length)]))

    @staticmethod
    def _backend_read_response_to_str(response):
        return create_string_buffer(response.encode('utf8'), len(response))

    @staticmethod
    def _backend_notify_response_to_str(response):
        return create_string_buffer(bytes(response), len(bytes(response)))


class Requester(GATTRequester):

    def __init__(self, notify_fcn, *args):
        GATTRequester.__init__(self, *args)
        self.notify_fcn = notify_fcn

    def on_notification(self, handle, data):
        return self.notify_fcn(handle, data)
