#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""

.. moduleauthor:: hbldh <henrik.blidh@nedomkull.com>
Created on 2016-04-08

"""
from __future__ import division
from __future__ import print_function
# from __future__ import unicode_literals
from __future__ import absolute_import

import os
import time
from ctypes import byref
import uuid

from pymetawear import libmetawear
from pymetawear.exceptions import PyMetaWearException
from pymetawear.mbientlab.metawear.core import BtleConnection, Fn_VoidPtr_GattCharPtr, \
    Fn_VoidPtr_GattCharPtr_ByteArray, Fn_VoidPtr_Int
from pymetawear.specs import METAWEAR_SERVICE_NOTIFY_CHAR
from pymetawear.utils import string_types


class BLECommunicationBackend(object):

    def __init__(self, address, interface=None,
                 async=True, timeout=None, debug=False):
        self._address = str(address)
        self._interface = str(interface)
        self._async = async
        self._debug = debug
        self._timeout = timeout

        self._initialization_status = -1

        self._requester = None

        self._build_handle_dict()

        # Define read and write to characteristics methods to be used by
        # libmetawear. These methods in their turn use the backend read/write
        # methods implemented in the specific backends.
        self._btle_connection = BtleConnection(
            write_gatt_char=Fn_VoidPtr_GattCharPtr_ByteArray(self.mbl_mw_write_gatt_char),
            read_gatt_char=Fn_VoidPtr_GattCharPtr(self.mbl_mw_read_gatt_char))

        # Dictionary of callbacks for subscriptions set up through the
        # libmetawear library.
        self.callbacks = {
            'initialization': (self._initialized_fcn,
                               Fn_VoidPtr_Int(self._initialized_fcn)),
        }

        # Setup the notification characteristic subscription
        # required by MetaWear.
        self._notify_char_handle = self.get_handle(
            METAWEAR_SERVICE_NOTIFY_CHAR[1])
        self.subscribe(METAWEAR_SERVICE_NOTIFY_CHAR[1],
                       self.handle_notify_char_output)

        # Now create a libmetawear board object and initialize it.
        self.board = libmetawear.mbl_mw_metawearboard_create(
            byref(self._btle_connection))

        _response_time = os.environ.get('PYMETAWEAR_RESPONSE_TIME', 300)
        libmetawear.mbl_mw_metawearboard_set_time_for_response(self.board, int(_response_time))

        libmetawear.mbl_mw_metawearboard_initialize(
            self.board, self.callbacks.get('initialization')[1])

    def __str__(self):
        return "{0}, {1}".format(self.__class__.__name__, self._address)

    def __repr__(self):
        return "<{0}, {1}>".format(self.__class__.__name__, self._address)

    def _build_handle_dict(self):
        pass

    @property
    def initialized(self):
        return self._initialization_status >= 0

    @property
    def requester(self):
        """The requester object for the backend used.

        :return: The connected requester instance.
        :rtype: :class:`bluetooth.ble.GATTRequester` or
            :class:`pygatt.device.BLEDevice`

        """
        raise NotImplementedError("Use backend-specific classes instead!")

    def disconnect(self):
        """Handle any required disconnecting in the backend,
        e.g. sever Bluetooth connection.
        """
        raise NotImplementedError("Use backend-specific classes instead!")

    def subscribe(self, characteristic_uuid, callback):
        self._subscribe(characteristic_uuid, callback)
        if self._debug:
            self._print_debug_output("Subscribe", characteristic_uuid, [])

    def mbl_mw_read_gatt_char(self, board, characteristic):
        """Read the desired data from the MetaWear board.

        :param pymetawear.mbientlab.metawear.core.GattCharacteristic
            characteristic: :class:`ctypes.POINTER` to a GattCharacteristic.

        """
        if isinstance(characteristic, uuid.UUID):
            service_uuid, characteristic_uuid = None, characteristic
        else:
            service_uuid, characteristic_uuid = self._mbl_mw_characteristic_2_uuids(
                characteristic.contents)
        response = self.read_gatt_char_by_uuid(characteristic_uuid)
        sb = self.read_response_to_str(response)
        libmetawear.mbl_mw_metawearboard_char_read(
            self.board, characteristic, sb.raw, len(sb.raw))

        if self._debug:
            self._print_debug_output("Read", characteristic_uuid, response)

    def mbl_mw_write_gatt_char(self, board, characteristic, command, length):
        """Write the desired data to the MetaWear board.

        :param pymetawear.mbientlab.metawear.core.GattCharacteristic
            characteristic: Characteristic to write to.
        :param POINTER command: The command to send, as a byte array pointer.
        :param int length: Length of the array that command points.

        """
        if isinstance(characteristic, uuid.UUID):
            service_uuid, characteristic_uuid = None, characteristic
        else:
            service_uuid, characteristic_uuid = self._mbl_mw_characteristic_2_uuids(
                characteristic.contents)
        data_to_send = self.mbl_mw_command_to_input(command, length)
        if self._debug:
            self._print_debug_output("Write", characteristic_uuid, data_to_send)
        self.write_gatt_char_by_uuid(characteristic_uuid, data_to_send)

    def _subscribe(self, characterisitic_uuid, callback):
        raise NotImplementedError("Use backend-specific classes instead!")

    def read_gatt_char_by_uuid(self, characteristic_uuid):
        raise NotImplementedError("Use backend-specific classes instead!")

    def write_gatt_char_by_uuid(self, characteristic_uuid, data_to_send):
        raise NotImplementedError("Use backend-specific classes instead!")

    # Callback methods

    def _initialized_fcn(self, board, status):
        if self._debug:
            print("{0} initialized with status {1}.".format(self, status))
        self._initialization_status = status

    def handle_notify_char_output(self, handle, value):
        if self._debug:
            self._print_debug_output("Notify", handle, value)

        if handle == self._notify_char_handle:
            sb = self.notify_response_to_str(value)
            libmetawear.mbl_mw_metawearboard_notify_char_changed(
                self.board, sb.raw, len(sb.raw))
        else:
            raise PyMetaWearException(
                "Notification on unexpected handle: {0}".format(handle))

    # Helper methods

    def get_handle(self, uuid, value_handle=True):
        """Get handle for a characteristic UUID.

        :param uuid.UUID uuid: The UUID to get handle of.
        :param bool notify_handle:
        :return: Integer handle corresponding to the input characteristic UUID.
        :rtype: int

        """
        raise NotImplementedError("Use backend-specific classes instead!")

    @staticmethod
    def mbl_mw_command_to_input(command, length):
        raise NotImplementedError("Use backend-specific classes instead!")

    @staticmethod
    def read_response_to_str(response):
        raise NotImplementedError("Use backend-specific classes instead!")

    @staticmethod
    def notify_response_to_str(response):
        raise NotImplementedError("Use backend-specific classes instead!")

    @staticmethod
    def _mbl_mw_characteristic_2_uuids(characteristic):
        return (uuid.UUID(int=(characteristic.service_uuid_high << 64) +
                               characteristic.service_uuid_low),
                uuid.UUID(int=(characteristic.uuid_high << 64) +
                               characteristic.uuid_low))

    def _print_debug_output(self, action, handle_or_char, data):
        if data and isinstance(data[0], int):
            data_as_hex = " ".join(["{:02x}".format(b) for b in data])
        else:
            data_as_hex = " ".join(["{:02x}".format(ord(b)) for b in data])

        if isinstance(handle_or_char, (uuid.UUID, string_types)):
            handle = self.get_handle(handle_or_char)
        elif isinstance(handle_or_char, int):
            handle = handle_or_char
        else:
            handle = -1

        print("{0:<6s} 0x{1:04x}: {2}".format(action, handle, data_as_hex))

    def sleep(self, t):
        """Make backend sleep."""
        time.sleep(t)
