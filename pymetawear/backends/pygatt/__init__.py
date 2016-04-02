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

        self.requester.subscribe(str(METAWEAR_SERVICE_NOTIFY_CHAR[1]), self._handle_notification)

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

    def _handle_notification(self, handle, value):
        if handle == self.get_handle(METAWEAR_SERVICE_NOTIFY_CHAR[1]):
            sb = self._notify_response_to_buffer(value)
            libmetawear.mbl_mw_connection_notify_char_changed(self.board, sb.raw, len(sb.raw))
        else:
            print("- notification on handle {0:04x}: {1}\n".format(handle, value))

    def _read_gatt_char(self, characteristic):
        """Read the desired data from the MetaWear board.

        :param pymetawear.mbientlab.metawear.core.GattCharacteristic characteristic: :class:`ctypes.POINTER`
            to a GattCharacteristic.
        :return: The read data.
        :rtype: str

        """
        service_uuid, characteristic_uuid = self._characteristic_2_uuids(characteristic.contents)
        response = self.requester.char_read(str(characteristic_uuid))

        if self._debug:
            print("Read  0x{0:02x}: {1}".format(self.get_handle(characteristic_uuid),
                                                " ".join([hex(b) for b in response])))

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
        data_to_send = self._command_to_str(command, length)
        if self._debug:
            print("Write 0x{0:02x}: {1}".format(self.get_handle(characteristic_uuid),
                                                " ".join([hex(b) for b in data_to_send])))
        self.requester.char_write(str(characteristic_uuid), data_to_send)

    def get_handle(self, uuid):
        return self.requester.get_handle(uuid)

    @staticmethod
    def _read_response_to_buffer(response):
        return create_string_buffer(str(response), len(response))

    @staticmethod
    def _command_to_str(command, length):
        return bytearray([command[i] for i in range_(length)])

    @staticmethod
    def _notify_response_to_buffer(response):
        return create_string_buffer(str(response), len(response))
