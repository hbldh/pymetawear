#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:mod:`pygatt`
==================

.. moduleauthor:: hbldh <henrik.blidh@nedomkull.com>
Created on 2016-04-02

"""

from __future__ import division
from __future__ import print_function
#from __future__ import unicode_literals
from __future__ import absolute_import

import uuid

from ctypes import create_string_buffer

from pymetawear.client import MetaWearClient, libmetawear, range_
from pymetawear.exceptions import PyMetaWearException, PyMetaWearConnectionTimeout
from pymetawear.specs import METAWEAR_SERVICE_NOTIFY_CHAR

try:
    import pygatt
    from pymetawear.backends.pygatt.gatttool import PyMetaWearGATTToolBackend
    __all__ = ["MetaWearClientPyGatt"]
except ImportError:
    __all__ = []
    pygatt = None


class MetaWearClientPyGatt(MetaWearClient):
    """
    Client using `pygatt <https://bitbucket.org/OscarAcena/pygattlib>`_
    for BLE communication.
    """

    def __init__(self, address, debug=False):

        if pygatt is None:
            raise PyMetaWearException('PyGATT client not available. Install pygatt first.')

        self._address = address
        self._debug = debug
        self._backend = None
        self._requester = None

        self.requester.subscribe(str(METAWEAR_SERVICE_NOTIFY_CHAR[1]), self._handle_notify_char_output)

        super(MetaWearClientPyGatt, self).__init__(address, debug)

    @property
    def requester(self):
        """Property handling `GattRequester` and its connection.

        :return: The connected GattRequester instance.
        :rtype: :class:`pygatt.device.BLEDevice`

        """
        if self._requester is None:
            if self._debug:
                print("Creating new GATTToolBackend and starting GATTtool process...")
            self._backend = PyMetaWearGATTToolBackend()
            self._backend.start(reset_on_start=False)
            if self._debug:
                print("Connecting GATTTool...")
            self._requester = self._backend.connect(self._address, timeout=10.0, address_type='random')

            if not self.requester._connected:
                raise PyMetaWearConnectionTimeout("Could not establish a connection to {0}.".format(self._address))

        return self._requester

    def _backend_read_gatt_char(self, characteristic_uuid):
        """Read the desired data from the MetaWear board using pygatt backend.

        :param pymetawear.mbientlab.metawear.core.GattCharacteristic characteristic: :class:`ctypes.POINTER`
            to a GattCharacteristic.
        :return: The read data.
        :rtype: str

        """
        return self.requester.char_read(str(characteristic_uuid))

    def _backend_write_gatt_char(self, characteristic_uuid, data_to_send):
        """Write the desired data to the MetaWear board using pygatt backend.

        :param uuid.UUID characteristic_uuid: The UUID to the characteristic to write to.
        :param str data_to_send: Data to send.

        """
        self.requester.char_write(str(characteristic_uuid), data_to_send)

    def get_handle(self, uuid):
        return self.requester.get_handle(uuid)

    @staticmethod
    def _backend_read_response_to_str(response):
        return create_string_buffer(str(response), len(response))

    @staticmethod
    def _mbl_mw_command_to_backend_input(command, length):
        return bytearray([command[i] for i in range_(length)])

    @staticmethod
    def _backend_notify_response_to_str(response):
        return create_string_buffer(str(response), len(response))
