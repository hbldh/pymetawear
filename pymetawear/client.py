#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:mod:`client`
==================

.. module:: client
    :platform: Unix, Windows
    :synopsis:

.. moduleauthor:: hbldh <henrik.blidh@nedomkull.com>

Created on 2015-09-16

"""

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import

import os
import sys

from ctypes import cdll, create_string_buffer, byref
from bluetooth.ble import GATTRequester, DiscoveryService

if os.environ.get('METAWEAR_LIB_SO_NAME') is not None:
    libmetawear = cdll.LoadLibrary(os.environ["METAWEAR_LIB_SO_NAME"])
else:
    libmetawear = cdll.LoadLibrary(
        os.pathjoin(os.path.abspath(os.path.basename(__file__)), 'libmetawear.so'))

from pymetawear import models
from pymetawear.mbientlab.metawear.core import BtleConnection, FnGattCharPtr, FnGattCharPtrByteArray, FnVoid


class MetaWearClient(object):
    def __init__(self, address):

        self._address = address
        self._requester = None
        self.__initialized = False
        self.requester.discover_primary()

        self._btle_connection = BtleConnection(write_gatt_char=FnGattCharPtrByteArray(self.write_gatt_char),
                                               read_gatt_char=FnGattCharPtr(self.read_gatt_char))

        self.board = libmetawear.mbl_mw_metawearboard_create(byref(self._btle_connection))
        libmetawear.mbl_mw_metawearboard_initialize(self.board, FnVoid(self._initialized))

    def __str__(self):
        return "MetaWearClient, {0}".format(self._address)

    def __repr__(self):
        return "<MetaWearClient, {0}>".format(self._address)

    def _initialized(self):
        print("{0} initialized.".format(self))
        self.__initialized = True

    @property
    def requester(self):
        if self._requester is None:
            print("Creating new GATTRequester...")
            self._requester = GATTRequester(self._address, False)

        if not self._requester.is_connected():
            print("Connecting GATTRequester...")
            self._requester.connect(True, channel_type='random')

        return self._requester

    def read_gatt_char(self, characteristic):
        """Read the desired data from teh MetaWear board.

        .. code-block: c

            uint64_t service_uuid_high;         ///< High 64 bits of the parent service uuid
            uint64_t service_uuid_low;          ///< Low 64 bits of the parent service uuid
            uint64_t uuid_high;                 ///< High 64 bits of the characteristic uuid
            uint64_t uuid_low;                  ///< Low 64 bits of the characteristic uuid

        :param pymetawear.mbientlab.metawear.core.GattCharacteristic characteristic:
        :return:
        :rtype:

        """
        service_uuid_high = characteristic.service_uuid_high
        service_uuid_low = characteristic.service_uuid_low
        uuid_high = characteristic.uuid_high
        uuid_low = characteristic.uuid_low

        return self.requester.read_by_uuid(uuid_low)

    def write_gatt_char(self, characteristic, command, length):
        """Write the desired data to the MetaWear board.

        .. code-block: c

            uint64_t service_uuid_high;         ///< High 64 bits of the parent service uuid
            uint64_t service_uuid_low;          ///< Low 64 bits of the parent service uuid
            uint64_t uuid_high;                 ///< High 64 bits of the characteristic uuid
            uint64_t uuid_low;                  ///< Low 64 bits of the characteristic uuid

        :param pymetawear.mbientlab.metawear.core.GattCharacteristic characteristic:
        :param str command: The command to send.
        :param int length: Length of command in bytes.
        :return:
        :rtype:
        """
        service_uuid_high = characteristic.service_uuid_high
        service_uuid_low = characteristic.service_uuid_low
        uuid_high = characteristic.uuid_high
        uuid_low = characteristic.uuid_low

        return self.requester.write_by_handle(uuid_low)


if __name__ == '__main__':
    # if len(sys.argv) < 2:
    #    print("Usage: {} <addr>".format(sys.argv[0]))
    #    sys.exit(1)

    address = 'FF:50:35:82:3B:5A'

    MetaWearClient(address)  # sys.argv[1])
    print("Done.")
