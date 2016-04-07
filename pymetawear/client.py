#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""

.. moduleauthor:: hbldh <henrik.blidh@nedomkull.com>
Created on 2016-03-30

"""

from __future__ import division
from __future__ import print_function
# from __future__ import unicode_literals
from __future__ import absolute_import

import os

import time
import subprocess
import signal
import copy

from ctypes import cdll, byref, cast, POINTER, c_uint, c_float, c_ubyte

from pymetawear.exceptions import *
from pymetawear.mbientlab.metawear.core import BtleConnection, FnGattCharPtr, \
    FnGattCharPtrByteArray, FnVoid, DataTypeId, CartesianFloat, \
    BatteryState, Tcs34725ColorAdc, FnDataPtr
from pymetawear.specs import *

if os.environ.get('METAWEAR_LIB_SO_NAME') is not None:
    libmetawear = cdll.LoadLibrary(os.environ["METAWEAR_LIB_SO_NAME"])
else:
    libmetawear = cdll.LoadLibrary(
        os.path.join(os.path.abspath(os.path.dirname(__file__)),
                     'libmetawear.so'))

try:
    # Python 2
    range_ = xrange
except NameError:
    # Python 3
    range_ = range


def discover_devices(timeout=5, only_metawear=True):
    """Discover Bluetooth Devices nearby.

    Using hcitool in subprocess, since DiscoveryService in pybluez/gattlib
    requires sudo, and hcitool can be allowed to do scan without elevated
    permission:

        $ sudo apt-get install libcap2-bin

    installs linux capabilities manipulation tools.

        $ sudo setcap 'cap_net_raw,cap_net_admin+eip' `which hcitool`

    sets the missing capabilities on the executable quite like the setuid bit.

    References:

    SE, hcitool without sudo:
    https://unix.stackexchange.com/questions/96106/bluetooth-le-scan-as-non-root
    SE, hcitool lescan with timeout.
    https://stackoverflow.com/questions/26874829/hcitool-lescan-will-not-print-in-real-time-to-a-file

    :param int timeout: Duration of scanning.
    :param bool only_metawear: If only addresses with the string 'metawear'
        in its name should be returned.
    :return: List of tuples with `(address, name)`.
    :rtype: list

    """
    p = subprocess.Popen(["hcitool", "lescan"], stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    time.sleep(timeout)
    os.kill(p.pid, signal.SIGINT)
    out, err = p.communicate()
    if len(out) == 0 and len(err) > 0:
        if err == b'Set scan parameters failed: Operation not permitted\n':
            raise PyMetaWearException("Missing capabilites for hcitool!")
        if err == b'Set scan parameters failed: Input/output error\n':
            raise PyMetaWearException("Could not perform scan.")
    ble_devices = list(set([tuple(x.split(' ')) for x in
                            filter(None, out.decode('utf8').split('\n')[1:])]))
    if only_metawear:
        return list(filter(lambda x: 'metawear' in x[1].lower(), ble_devices))
    else:
        return ble_devices


class MetaWearClient(object):
    """
    MetaWear client bridging the gap between 
    `libmetawear` and a GATT communication client.
    """

    def __init__(self, address, debug=False):

        self._address = address
        self._debug = debug
        self._initialized = False

        self._notification_callbacks = {
            'initialization': (self._initialized_fcn,
                               FnVoid(self._initialized_fcn)),
        }

        self.sensor_data_handler = FnDataPtr(self._sensor_data_handler)

        self._btle_connection = BtleConnection(
            write_gatt_char=FnGattCharPtrByteArray(self.write_gatt_char),
            read_gatt_char=FnGattCharPtr(self.read_gatt_char))

        self.board = libmetawear.mbl_mw_metawearboard_create(
            byref(self._btle_connection))
        libmetawear.mbl_mw_metawearboard_initialize(
            self.board, self._notification_callbacks.get('initialization')[1])

        if self._debug:
            print("Waiting for MetaWear board to be fully initialized...")

        while not (libmetawear.mbl_mw_metawearboard_is_initialized(
                self.board) and self._initialized):
            time.sleep(0.1)

        self.firmware_version = tuple(
            [int(x) for x in self._backend_read_gatt_char(
             DEV_INFO_FIRMWARE_CHAR[1]).split('.')])
        self.model_version = int(self._backend_read_gatt_char(
            DEV_INFO_MODEL_CHAR[1]))

    def __str__(self):
        return "MetaWearClient, {0}".format(self._address)

    def __repr__(self):
        return "<MetaWearClient, {0}>".format(self._address)

    # Connection methods

    @property
    def requester(self):
        """The requester object for the backend used.

        :return: The connected GattRequester instance.
        :rtype: :class:`bluetooth.ble.GATTRequester` or 
            :class:`pygatt.device.BLEDevice`

        """
        raise NotImplementedError("Use backend-specific classes instead!")

    def disconnect(self):
        """Disconnects this client from the MetaWear board."""
        libmetawear.mbl_mw_metawearboard_tear_down(self.board)
        libmetawear.mbl_mw_metawearboard_free(self.board)
        self._backend_disconnect()

    def _backend_disconnect(self):
        """Handle any required disconnecting in the backend, 
        e.g. sever Bluetooth connection.
        """
        raise NotImplementedError("Use backend-specific classes instead!")

    # Callback methods

    def _initialized_fcn(self):
        if self._debug:
            print("{0} initialized.".format(self))
        self._initialized = True

    def _handle_notify_char_output(self, handle, value):
        if self._debug:
            self._print_debug_output("Notify", handle, value)

        if handle == self.get_handle(METAWEAR_SERVICE_NOTIFY_CHAR[1]):
            sb = self._backend_notify_response_to_str(value)
            libmetawear.mbl_mw_connection_notify_char_changed(
                self.board, sb.raw, len(sb.raw))
        else:
            raise PyMetaWearException(
                "Notification on unexpected handle: {0}".format(handle))

    # Read and Write methods

    def read_gatt_char(self, characteristic):
        """Read the desired data from the MetaWear board.

        :param pymetawear.mbientlab.metawear.core.GattCharacteristic 
            characteristic: :class:`ctypes.POINTER` to a GattCharacteristic.

        """
        service_uuid, characteristic_uuid = self._mbl_mw_characteristic_2_uuids(
            characteristic.contents)
        response = self._backend_read_gatt_char(characteristic_uuid)
        sb = self._backend_read_response_to_str(response)
        libmetawear.mbl_mw_connection_char_read(
            self.board, characteristic, sb.raw, len(sb.raw))

        if self._debug:
            self._print_debug_output("Read", characteristic_uuid, response)

    def _backend_read_gatt_char(self, characteristic):
        raise NotImplementedError("Use backend-specific classes instead!")

    def write_gatt_char(self, characteristic, command, length):
        """Write the desired data to the MetaWear board.

        :param pymetawear.mbientlab.metawear.core.GattCharacteristic 
            characteristic: Characteristic to write to.
        :param POINTER command: The command to send, as a byte array pointer.
        :param int length: Length of the array that command points.

        """
        service_uuid, characteristic_uuid = self._mbl_mw_characteristic_2_uuids(
            characteristic.contents)
        data_to_send = self._mbl_mw_command_to_backend_input(command, length)
        if self._debug:
            self._print_debug_output("Write", characteristic_uuid, data_to_send)
        self._backend_write_gatt_char(characteristic_uuid, data_to_send)

    def _backend_write_gatt_char(self, characteristic_uuid, data_to_send):
        raise NotImplementedError("Use backend-specific classes instead!")

    # MetaWear methods

    def switch_notifications(self, callback=None):
        """Subscribe or unsubscribe to switch notifications.

        Convenience method for handling switch usage.

        Example:

        .. code-block:: python

            from ctypes import POINTER, c_uint, cast

            def switch_callback(data):
                data_ptr = cast(data.contents.value, POINTER(c_uint))
                if data_ptr.contents.value == 1:
                    print("Switch pressed!")
                elif data_ptr.contents.value == 0:
                    print("Switch released!")

            mwclient.switch_notifications(switch_callback)

        :param callable callback: Switch notification callback function.
            If `None`, unsubscription to switch notifications is registered.

        """
        if callback is not None:
            data_signal = libmetawear.mbl_mw_switch_get_state_data_signal(
                self.board)
            self._data_signal_subscription(data_signal, 'switch', callback)
        else:
            self._data_signal_subscription(None, 'switch', callback)

    def _data_signal_subscription(self, data_signal, signal_name, callback):
        """Handle subscriptions to data signals on the MetaWear board.

        :param int data_signal: The ``libmetawear`` ID of the data signal.
        :param str signal_name: Key value to use for storing the callback.
        :param callable callback: The function to call when
            data signal notification arrives.

        """
        if callback is not None:
            if self._notification_callbacks.get(signal_name) is not None:
                raise PyMetaWearException(
                    "Subscription to {0} signal already in place!")
            self._notification_callbacks[signal_name] = (callback,
                                                         FnDataPtr(callback))
            libmetawear.mbl_mw_datasignal_subscribe(
                data_signal, self._notification_callbacks['switch'][1])
            if self._debug:
                print("Subscribing to {0} changes.".format(signal_name))
        else:
            if self._notification_callbacks.get(signal_name) is None:
                return
            data_signal = libmetawear.mbl_mw_switch_get_state_data_signal(
                self.board)
            libmetawear.mbl_mw_datasignal_unsubscribe(data_signal)
            self._notification_callbacks.pop('switch')
            if self._debug:
                print("Unsubscribing to {0} changes.".format(signal_name))

    # Helper methods

    def get_handle(self, uuid):
        """Get handle for a characteristic UUID.

        :param uuid.UUID uuid: The UUID to get handle of.
        :return: Integer handle corresponding to the input characteristic UUID.
        :rtype: int

        """
        raise NotImplementedError("Use backend-specific classes instead!")

    def _sensor_data_handler(self, data):
        if (data.contents.type_id == DataTypeId.UINT32):
            data_ptr = cast(data.contents.value, POINTER(c_uint))
            if self._debug:
                print(
                    "Sensor data received: {0}".format(data_ptr.contents.value))
            return data_ptr.contents.value
        elif (data.contents.type_id == DataTypeId.FLOAT):
            data_ptr = cast(data.contents.value, POINTER(c_float))
            if self._debug:
                print(
                    "Sensor data received: {0}".format(data_ptr.contents.value))
            return data_ptr.contents.value
        elif (data.contents.type_id == DataTypeId.CARTESIAN_FLOAT):
            data_ptr = cast(data.contents.value, POINTER(CartesianFloat))
            if self._debug:
                print("Sensor data received: {0}".format(data_ptr.contents))
            return copy.deepcopy(data_ptr.contents)
        elif (data.contents.type_id == DataTypeId.BATTERY_STATE):
            data_ptr = cast(data.contents.value, POINTER(BatteryState))
            if self._debug:
                print("Sensor data received: {0}".format(data_ptr.contents))
            return copy.deepcopy(data_ptr.contents)
        elif (data.contents.type_id == DataTypeId.BYTE_ARRAY):
            data_ptr = cast(data.contents.value,
                            POINTER(c_ubyte * data.contents.length))
            data_byte_array = []
            for i in range(0, data.contents.length):
                data_byte_array.append(data_ptr.contents[i])
            if self._debug:
                print("Sensor data received: {0}".format(data_byte_array))
            return data_byte_array
        elif (data.contents.type_id == DataTypeId.TCS34725_ADC):
            data_ptr = cast(data.contents.value, POINTER(Tcs34725ColorAdc))
            if self._debug:
                print("Sensor data received: {0}".format(data_ptr.contents))
            return copy.deepcopy(data_ptr.contents)
        else:
            raise RuntimeError(
                'Unrecognized data type id: ' + str(data.contents.type_id))

    @staticmethod
    def _mbl_mw_characteristic_2_uuids(characteristic):
        return (uuid.UUID(int=(characteristic.service_uuid_high << 64) +
                              characteristic.service_uuid_low),
                uuid.UUID(int=(characteristic.uuid_high << 64) +
                              characteristic.uuid_low))

    @staticmethod
    def _mbl_mw_command_to_backend_input(command, length):
        raise NotImplementedError("Use backend-specific classes instead!")

    @staticmethod
    def _backend_read_response_to_str(response):
        raise NotImplementedError("Use backend-specific classes instead!")

    @staticmethod
    def _backend_notify_response_to_str(response):
        raise NotImplementedError("Use backend-specific classes instead!")

    def _print_debug_output(self, action, handle_or_char, data):
        if isinstance(data, bytearray):
            data_as_hex = " ".join(["{:02x}".format(b) for b in data])
        else:
            data_as_hex = " ".join(["{:02x}".format(ord(b)) for b in data])

        if isinstance(handle_or_char, (uuid.UUID, basestring)):
            handle = self.get_handle(handle_or_char)
        elif isinstance(handle_or_char, int):
            handle = handle_or_char
        else:
            handle = -1

        print("{0:<6s} 0x{1:04x}: {2}".format(action, handle, data_as_hex))
