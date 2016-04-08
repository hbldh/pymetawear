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

from ctypes import cast, POINTER, c_uint, c_float, c_ubyte

from pymetawear import libmetawear
from pymetawear.exceptions import *
from pymetawear.mbientlab.metawear.core import DataTypeId, CartesianFloat, \
    BatteryState, Tcs34725ColorAdc, FnDataPtr
from pymetawear.specs import *
from pymetawear.backends.pygatt import PyGattBackend
from pymetawear.backends.pybluez import PyBluezBackend


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

    def __init__(self, address, backend='pygatt', debug=False):

        self._address = address
        self._debug = debug
        self._initialized = False

        self._backend = None

        if backend == 'pygatt':
            self._backend = PyGattBackend(
                self._address, debug=debug)
        elif backend == 'pybluez':
            self._backend = PyBluezBackend(
                self._address, debug=debug)

        if self._debug:
            print("Waiting for MetaWear board to be fully initialized...")

        while not (libmetawear.mbl_mw_metawearboard_is_initialized(
                self.board) and self.backend.initialized):
            time.sleep(0.1)

        self.firmware_version = tuple(
            [int(x) for x in self.backend._read_gatt_char(
             DEV_INFO_FIRMWARE_CHAR[1]).split('.')])
        self.model_version = int(self.backend._read_gatt_char(
            DEV_INFO_MODEL_CHAR[1]))

    def __str__(self):
        return "MetaWearClient, {0}".format(self._address)

    def __repr__(self):
        return "<MetaWearClient, {0}>".format(self._address)

    # Connection methods

    @property
    def backend(self):
        """The requester object for the backend used.

        :return: The connected BLE backend.
        :rtype: :class:`pymetawear.backend.BLECommunicationBackend`

        """
        return self._backend

    @property
    def board(self):
        return self.backend.board

    def disconnect(self):
        """Disconnects this client from the MetaWear board."""
        libmetawear.mbl_mw_metawearboard_tear_down(self.board)
        libmetawear.mbl_mw_metawearboard_free(self.board)
        self.backend.disconnect()

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
            if self.backend.notification_callbacks.get(signal_name) is not None:
                raise PyMetaWearException(
                    "Subscription to {0} signal already in place!")
            self.backend.notification_callbacks[signal_name] = (callback,
                                                         FnDataPtr(callback))
            libmetawear.mbl_mw_datasignal_subscribe(
                data_signal, self.backend.notification_callbacks['switch'][1])
            if self._debug:
                print("Subscribing to {0} changes.".format(signal_name))
        else:
            if self.backend.notification_callbacks.get(signal_name) is None:
                return
            data_signal = libmetawear.mbl_mw_switch_get_state_data_signal(
                self.board)
            libmetawear.mbl_mw_datasignal_unsubscribe(data_signal)
            self.backend.notification_callbacks.pop('switch')
            if self._debug:
                print("Unsubscribing to {0} changes.".format(signal_name))

    # Helper methods

    def get_handle(self, uuid, notify_handle=False):
        """Get handle for a characteristic UUID.

        :param uuid.UUID uuid: The UUID to get handle of.
        :param bool notify_handle:
        :return: Integer handle corresponding to the input characteristic UUID.
        :rtype: int

        """
        return self.backend.get_handle(uuid, notify_handle=notify_handle)

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
