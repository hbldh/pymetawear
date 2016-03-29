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
        os.pathjoin(os.path.abspath(os.path.basename(__file__)), 'libmetawear.so.0.3.0'))

from pymetawear import models
from pymetawear.mbientlab.metawear.core import BtleConnection, FnGattCharPtr, FnGattCharPtrByteArray, FnVoid


class MetaWearClient(object):
    def __init__(self, address=None, ):

        if address is None:
            ds = DiscoveryService()
            out = ds.discover(2)
            address = out.keys()[0]

        self.requester = GATTRequester(address, False)
        self.connect()
        self.request_data()

        self.firmware_revision = create_string_buffer(b'1.1.0', 5)

        self._send_command_fn = FnGattCharPtrByteArray(self.commandLogger)
        self._read_gatt_char_fn = FnGattCharPtr(self.read_gatt_char)
        self._btle_connection = BtleConnection(write_gatt_char=self._send_command_fn,
                                               read_gatt_char=self._read_gatt_char_fn)

        self._board_type = models.MetaWearBoard()
        self.board = libmetawear.mbl_mw_metawearboard_create(byref(self._btle_connection))
        libmetawear.mbl_mw_metawearboard_initialize(self.board, FnVoid(self._initialized))

    def _initialized(self):
        self.__initialized = True

    def connect(self):
        print("Connecting...", end=' ')
        sys.stdout.flush()

        self.requester.connect(True)
        print("OK!")

    def request_data(self):
        data = self.requester.read_by_uuid(
            "00002a00-0000-1000-8000-00805f9b34fb")[0]
        try:
            print("Device name: " + data.decode("utf-8"))
        except AttributeError:
            print("Device name: " + data)

    def read_gatt_char(self, characteristic):
        if (characteristic.contents.uuid_high == 0x00002a2400001000 and
                    characteristic.contents.uuid_low == 0x800000805f9b34fb):
            model_number = self._board_type.model_nbr

            libmetawear.mbl_mw_connection_char_read(self.board, characteristic, model_number.raw, len(model_number.raw))
        elif (
                characteristic.contents.uuid_high == 0x00002a2600001000 and characteristic.contents.uuid_low == 0x800000805f9b34fb):
            libmetawear.mbl_mw_connection_char_read(self.board, characteristic, self.firmware_revision.raw,
                                                    len(self.firmware_revision.raw))


if __name__ == '__main__':
    # if len(sys.argv) < 2:
    #    print("Usage: {} <addr>".format(sys.argv[0]))
    #    sys.exit(1)

    address = 'FF:50:35:82:3B:5A'

    MetaWearClient(address)  # sys.argv[1])
    print("Done.")
