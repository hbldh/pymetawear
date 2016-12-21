#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""

.. moduleauthor:: hbldh <henrik.blidh@nedomkull.com>
Created on 2016-04-08

"""
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import os
import time
from ctypes import byref
import uuid
import logging

from pymetawear import libmetawear
from pymetawear.exceptions import PyMetaWearException
from pymetawear.mbientlab.metawear.core import BtleConnection, \
    Fn_VoidPtr_GattCharPtr, \
    Fn_VoidPtr_GattCharPtr_ByteArray, Fn_VoidPtr_Int
from pymetawear.specs import METAWEAR_SERVICE_NOTIFY_CHAR
from pymetawear.compat import string_types, range_

log = logging.getLogger(__name__)


class BLECommunicationBackend(object):
    def __init__(self, address, interface=None, timeout=None, debug=False):
        self._address = str(address)
        self._interface = str(interface)
        self._debug = debug
        self._timeout = timeout

        if debug:
            log.setLevel(logging.DEBUG)

        self.initialization_status = -1

        self._requester = None

        # Define read and write to characteristics methods to be used by
        # libmetawear. These methods in their turn use the backend read/write
        # methods implemented in the specific backends.
        self._btle_connection = BtleConnection(
            write_gatt_char=Fn_VoidPtr_GattCharPtr_ByteArray(
                self.mbl_mw_write_gatt_char),
            read_gatt_char=Fn_VoidPtr_GattCharPtr(self.mbl_mw_read_gatt_char))

        # Dictionary of callbacks for subscriptions set up through the
        # libmetawear library.
        self.callbacks = {
            'initialization': (self._initialized_fcn,
                               Fn_VoidPtr_Int(self._initialized_fcn)),
        }

        self.board = None
        self._notify_char_handle = None

    def __str__(self):
        return "{0}, {1}".format(self.__class__.__name__, self._address)

    def __repr__(self):
        return "<{0}, {1}>".format(self.__class__.__name__, self._address)

    def _build_handle_dict(self):
        pass

    @property
    def initialized(self):
        return self.initialization_status >= 0

    @property
    def is_connected(self):
        raise NotImplementedError("Use backend-specific classes instead!")

    @property
    def requester(self):
        """The requester object for the backend used.

        :return: The connected requester instance.
        :rtype: :class:`bluetooth.ble.GATTRequester` or
            :class:`pygatt.device.BLEDevice`

        """
        raise NotImplementedError("Use backend-specific classes instead!")

    def connect(self, clean_connect=False):
        self._build_handle_dict()

        # Setup the notification characteristic subscription
        # required by MetaWear.
        self._notify_char_handle = self.get_handle(
            METAWEAR_SERVICE_NOTIFY_CHAR[1])
        self.subscribe(METAWEAR_SERVICE_NOTIFY_CHAR[1],
                       self.handle_notify_char_output)

        # Now create a libmetawear board object and initialize it.
        # Free memory for any old board first.
        if self.board is not None:
            try:
                libmetawear.mbl_mw_metawearboard_tear_down(self.board)
            except:
                pass
            libmetawear.mbl_mw_metawearboard_free(self.board)
        self.board = libmetawear.mbl_mw_metawearboard_create(
            byref(self._btle_connection))

        _response_time = os.environ.get('PYMETAWEAR_RESPONSE_TIME', 300)
        libmetawear.mbl_mw_metawearboard_set_time_for_response(self.board, int(
            _response_time))

        libmetawear.mbl_mw_metawearboard_initialize(
            self.board, self.callbacks.get('initialization')[1])

    def disconnect(self):
        """Handle any required disconnecting in the backend,
        e.g. sever Bluetooth connection.
        """
        raise NotImplementedError("Use backend-specific classes instead!")

    def subscribe(self, characteristic_uuid, callback):
        self._subscribe(characteristic_uuid, callback)
        self._log("Subscribe", characteristic_uuid, [], 0)

    def mbl_mw_read_gatt_char(self, board, characteristic):
        """Read the desired data from the MetaWear board.

        :param pymetawear.mbientlab.metawear.core.GattCharacteristic
            characteristic: :class:`ctypes.POINTER` to a GattCharacteristic.

        """
        response = self.read_gatt_char_by_uuid(characteristic)
        sb = self._response_2_string_buffer(response)
        libmetawear.mbl_mw_metawearboard_char_read(
            self.board, characteristic, sb.raw, len(sb.raw))

        self._log("Read", characteristic, response, len(response))

    def mbl_mw_write_gatt_char(self, board, characteristic, command, length):
        """Write the desired data to the MetaWear board.

        :param pymetawear.mbientlab.metawear.core.GattCharacteristic
            characteristic: Characteristic to write to.
        :param POINTER command: The command to send, as a byte array pointer.
        :param int length: Length of the array that command points.

        """
        self._log("Write", characteristic, command, length)
        self.write_gatt_char_by_uuid(characteristic, command, length)

    # Helper methods

    @staticmethod
    def get_uuid(characteristic):
        if isinstance(characteristic, uuid.UUID):
            return characteristic
        else:
            return uuid.UUID(int=(characteristic.contents.uuid_high << 64) +
                             characteristic.contents.uuid_low)

    @staticmethod
    def get_service_uuid(characteristic):
        if isinstance(characteristic, uuid.UUID):
            return characteristic
        else:
            return uuid.UUID(int=(characteristic.contents.service_uuid_high << 64) +
                             characteristic.contents.service_uuid_low)

    def sleep(self, t):
        """Make backend sleep."""
        time.sleep(t)

    #  Callback methods

    def _initialized_fcn(self, board, status):
        log.debug("{0} initialized with status {1}.".format(self, status))
        self.initialization_status = status

    def handle_notify_char_output(self, handle, value):

        self._log("Notify", handle, value, 0)

        if handle == self._notify_char_handle:
            sb = self._response_2_string_buffer(value)
            libmetawear.mbl_mw_metawearboard_notify_char_changed(
                self.board, sb.raw, len(sb.raw))
        else:
            raise PyMetaWearException(
                "Notification on unexpected handle: {0}".format(handle))

    # Methods to be implemented by backends.

    def _subscribe(self, characterisitic_uuid, callback):
        raise NotImplementedError("Use backend-specific classes instead!")

    def read_gatt_char_by_uuid(self, characteristic):
        raise NotImplementedError("Use backend-specific classes instead!")

    def write_gatt_char_by_uuid(self, characteristic, command, length):
        raise NotImplementedError("Use backend-specific classes instead!")

    def get_handle(self, uuid, notify_handle=False):
        """Get handle for a characteristic UUID.

        :param uuid.UUID uuid: The UUID to get handle of.
        :param bool notify_handle:
        :return: Integer handle corresponding to the input characteristic UUID.
        :rtype: int

        """
        raise NotImplementedError("Use backend-specific classes instead!")

    def _response_2_string_buffer(self, response):
        raise NotImplementedError("Use backend-specific classes instead!")

    # Debug method

    def _log(self, action, handle_or_char, value, value_length):

        if not self._debug:
            return

        if action == "Write":
            data_as_hex = " ".join(["{:02x}".format(b) for
                                    b in [value[i] for i in range_(value_length)]])
        elif action == "Subscribe":
            data_as_hex = ""
        else:
            data_as_hex = " ".join(["{:02x}".format(ord(b)) for
                                    b in self._response_2_string_buffer(value)])

        if isinstance(handle_or_char, (uuid.UUID, string_types)):
            handle = self.get_handle(handle_or_char)
        elif isinstance(handle_or_char, int):
            handle = handle_or_char
        else:
            # Assume it is a Pointer to a GattCharacteristic...
            try:
                handle = self.get_handle(self.get_uuid(handle_or_char))
            except:
                handle = -1

        log.debug("{0:<6s} 0x{1:04x}: {2}".format(action, handle, data_as_hex))
