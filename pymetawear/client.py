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
import warnings

from ctypes import cast, POINTER, c_uint, c_float, c_ubyte, c_long, c_uint16

from pymetawear import libmetawear, specs
from pymetawear.exceptions import *
from pymetawear.mbientlab.metawear.core import DataTypeId, CartesianFloat, \
    BatteryState, Tcs34725ColorAdc, FnDataPtr
import pymetawear.modules
import pymetawear.modules.accelerometer
from pymetawear.utils import is_64bit

from pymetawear.backends.pygatt import PyGattBackend
from pymetawear.backends.pybluez import PyBluezBackend


def discover_devices(timeout=5, only_metawear=True):
    """Discover Bluetooth Devices nearby.

    Using hcitool in subprocess, since DiscoveryService in pybluez/gattlib
    requires sudo, and hcitool can be allowed to do scan without elevated
    permission.

    .. code-block:: bash

        $ sudo apt-get install libcap2-bin

    installs linux capabilities manipulation tools.

    .. code-block:: bash

        $ sudo setcap 'cap_net_raw,cap_net_admin+eip' `which hcitool`

    sets the missing capabilities on the executable quite like the setuid bit.

    **References:**

    * `StackExchange, hcitool without sudo <https://unix.stackexchange.com/questions/96106/bluetooth-le-scan-as-non-root>`_
    * `StackOverflow, hcitool lescan with timeout <https://stackoverflow.com/questions/26874829/hcitool-lescan-will-not-print-in-real-time-to-a-file>`_

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
    """A MetaWear communication client.

    This client bridges the gap between the
    `MetaWear C++ API <https://github.com/mbientlab/Metawear-CppAPI>`_
    and a GATT communication package in Python. It provides Pythonic
    interface to using the MetaWear boards, allowing for rapid
    development and testing.

    :param str address: A Bluetooth MAC address to a MetaWear board.
    :param str backend: Either ``pygatt`` or ``pybluez``, designating which
        BLE communication backend that should be used.
    :param bool debug: If printout of all sent and received
        data should be done.

    """

    def __init__(self, address, backend='pygatt', debug=False):
        """Constructor."""
        self._address = address
        self._debug = debug
        self._initialized = False
        self._64bit = is_64bit()

        self.sensor_data_handler = FnDataPtr(self._sensor_data_handler)

        if backend == 'pygatt':
            self._backend = PyGattBackend(
                self._address, debug=debug)
        elif backend == 'pybluez':
            self._backend = PyBluezBackend(
                self._address, debug=debug)
        else:
            raise PyMetaWearException("Unknown backend: {0}".format(backend))

        if self._debug:
            print("Waiting for MetaWear board to be fully initialized...")

        while not (libmetawear.mbl_mw_metawearboard_is_initialized(
                self.board) and self.backend.initialized):
            time.sleep(0.1)

        self.firmware_version = tuple(
            [int(x) for x in self.backend.read_gatt_char_by_uuid(
            specs.DEV_INFO_FIRMWARE_CHAR[1]).decode().split('.')])
        self.model_version = int(self.backend.read_gatt_char_by_uuid(
            specs.DEV_INFO_MODEL_CHAR[1]).decode())

        self._accelerometer_specs = pymetawear.modules.accelerometer.PyMetaWearAccelerometer(
            libmetawear.mbl_mw_metawearboard_lookup_module(
                pymetawear.modules.Modules.MBL_MW_MODULE_ACCELEROMETER))

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

    # Sensor methods

    def accelerometer_notifications(self, callback):
        """Subscribe or unsubscribe to accelerometer notifications.

        :param callable callback: Accelerometer data notification callback
            function. If `None`, unsubscription to accelerometer notifications
            is registered.

        """
        data_signal = self._data_signal_preprocess(
            libmetawear.mbl_mw_acc_get_acceleration_data_signal)
        self._data_signal_subscription(data_signal, 'accelerometer', callback)

    def set_accelerometer_settings(self, data_rate=None, data_range=None):
        """Set accelerometer settings.

         Can be called with two or only one setting:

         .. code-block:: python

            mwclient.set_accelerometer_settings(data_rate=200.0, data_range=8.0)

        will give the same result as

        .. code-block:: python

            mwclient.set_accelerometer_settings(data_rate=200.0)
            mwclient.set_accelerometer_settings(data_range=8.0)

        albeit that the latter example makes two writes to the board.

        Call :meth:`~get_available_accelerometer_settings` to see which values
        that can be set.

        :param float data_rate: The frequency of accelerometer updates in Hz.
        :param float data_range: The measurement range in the unit ``g``.

        """
        if data_rate is not None:
            odr = self._accelerometer_specs.get_odr(data_rate)
            if self._debug:
                print("Setting Accelerometer ODR to {0}".format(odr))
            libmetawear.mbl_mw_acc_set_odr(self.board, c_float(odr))
        if data_range is not None:
            fsr = self._accelerometer_specs.get_fsr(data_range)
            if self._debug:
                print("Setting Accelerometer FSR to {0}".format(fsr))
            libmetawear.mbl_mw_acc_set_range(self.board, c_float(fsr))

        if (data_rate is not None) or (data_range is not None):
            libmetawear.mbl_mw_acc_write_acceleration_config(self.board)

    def get_available_accelerometer_settings(self):
        return self._accelerometer_specs

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
        data_signal = self._data_signal_preprocess(
            libmetawear.mbl_mw_switch_get_state_data_signal)
        self._data_signal_subscription(data_signal, 'switch', callback)

    def battery_notifications(self, callback=None):
        """Subscribe or unsubscribe to battery notifications.

        :param callable callback: Battery data notification callback
            function. If `None`, unsubscription to battery notifications
            is registered.

        """
        data_signal = self._data_signal_preprocess(
            libmetawear.mbl_mw_settings_get_battery_state_data_signal)
        self._data_signal_subscription(data_signal, 'battery', callback)

    def read_battery_state(self):
        """Triggers a battery state notification.

        N.B. that a :meth:`~battery_notifications` call that registers a callback for
        battery state should have been done prior to calling this method.

        """
        if self.backend.callbacks.get('battery') is None:
            warnings.warn("No battery callback is registered!", RuntimeWarning)
        libmetawear.mbl_mw_settings_read_battery_state(self.board)

    def haptic_start_motor(self, duty_cycle_per, pulse_width_ms):
        """Activate the haptic motor.

        :param float duty_cycle_per: Strength of the motor,
            between [0, 100] percent
        :param int pulse_width_ms: How long to run the motor, in milliseconds

        """
        libmetawear.mbl_mw_haptic_start_motor(
            c_float(float(duty_cycle_per)),
            c_uint16(int(pulse_width_ms)))

    def haptic_start_buzzer(self, pulse_width_ms):
        """Activate the haptic buzzer.

        :param int pulse_width_ms: How long to run the motor, in milliseconds

        """
        libmetawear.mbl_mw_haptic_start_buzzer(
            c_uint16(int(pulse_width_ms)))

    def _data_signal_preprocess(self, data_signal_func):
        if self._64bit:
            data_signal_func.restype = c_long
            data_signal = c_long(data_signal_func(self.board))
        else:
            data_signal = data_signal_func(self.board)
        return data_signal

    def _data_signal_subscription(self, data_signal, signal_name, callback):
        """Handle subscriptions to data signals on the MetaWear board.

        :param int data_signal: The ``libmetawear`` ID of the data signal.
        :param str signal_name: Key value to use for storing the callback.
        :param callable callback: The function to call when
            data signal notification arrives.

        """
        if callback is not None:
            if self._debug:
                print("Subscribing to {0} changes. (Sig#: {1})".format(
                    signal_name, data_signal))
            if self.backend.callbacks.get(signal_name) is not None:
                raise PyMetaWearException(
                    "Subscription to {0} signal already in place!")
            self.backend.callbacks[signal_name] = \
                (callback, FnDataPtr(callback))
            libmetawear.mbl_mw_datasignal_subscribe(
                data_signal, self.backend.callbacks[signal_name][1])
        else:
            if self._debug:
                print("Unsubscribing to {0} changes. (Sig#: {1})".format(
                    signal_name, data_signal))
            if self.backend.callbacks.get(signal_name) is None:
                return
            libmetawear.mbl_mw_datasignal_unsubscribe(data_signal)
            self.backend.callbacks.pop(signal_name)

    def set_logging_state(self, enabled=False):
        if enabled:
            libmetawear.mbl_mw_logging_start(self.board)
        else:
            libmetawear.mbl_mw_logging_stop(self.board)

    def download_log(self, n_notifies):
        libmetawear.mbl_mw_logging_download(self.board, n_notifies)

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
