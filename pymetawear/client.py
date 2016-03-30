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
#from __future__ import unicode_literals
from __future__ import absolute_import

import os

import time
import subprocess
import signal
import uuid
import copy

from ctypes import cdll, byref, cast, POINTER, c_uint, c_float, c_ubyte
from bluetooth.ble import GATTRequester

if os.environ.get('METAWEAR_LIB_SO_NAME') is not None:
    libmetawear = cdll.LoadLibrary(os.environ["METAWEAR_LIB_SO_NAME"])
else:
    libmetawear = cdll.LoadLibrary(
        os.path.join(os.path.abspath(os.path.dirname(__file__)), 'libmetawear.so'))

from pymetawear.exceptions import *
from pymetawear.mbientlab.metawear.core import BtleConnection, FnGattCharPtr, FnGattCharPtrByteArray, \
    FnVoid, DataTypeId, CartesianFloat, BatteryState, Tcs34725ColorAdc, FnDataPtr


def discover_devices(timeout=5, interface="hci0", only_metawear=True):
    """Discover Bluetooth Devices nearby.

    Using hcitool in subprocess, since DiscoveryService in pybluez/gattlib requires sudo,
    and hcitool can be allowed to do scan without elevated permission:

        $> sudo apt-get install libcap2-bin

    installs linux capabilities manipulation tools.

        $> sudo setcap 'cap_net_raw,cap_net_admin+eip' `which hcitool`

    sets the missing capabilities on the executable quite like the setuid bit.

    References:

    SE, hcitool without sudo:
    https://unix.stackexchange.com/questions/96106/bluetooth-le-scan-as-non-root
    SE, hcitool lescan with timeout.
    https://stackoverflow.com/questions/26874829/hcitool-lescan-will-not-print-in-real-time-to-a-file

    :param int timeout: Duration of scanning.
    :param str interface: Which interface to use for scanning.
    :param bool only_metawear: If only addresses with the string 'metawear' in its name should be returned.
    :return: List of tuples with `(address, name)`.
    :rtype: list

    """
    p = subprocess.Popen(["hcitool", "-i", interface, "lescan"], stdout=subprocess.PIPE)
    time.sleep(timeout)
    os.kill(p.pid, signal.SIGINT)
    ut = p.communicate()[0]
    ble_devices = list(set([tuple(x.split(' ')) for x in filter(None, ut.split('\n')[1:])]))
    if only_metawear:
        return filter(lambda x: 'metawear' in x[1].lower(), ble_devices)
    else:
        return ble_devices


class MetaWearClient(object):
    """MetaWear client bridging the gap between `libmetawear` and pybluez/gattlib."""

    def __init__(self, address, debug=False):

        self._address = address
        self._debug = debug
        self._requester = None
        self.__initialized = False

        self._btle_connection = BtleConnection(write_gatt_char=FnGattCharPtrByteArray(self.write_gatt_char),
                                               read_gatt_char=FnGattCharPtr(self.read_gatt_char))
        self.sensor_data_handler = FnDataPtr(self._sensor_data_handler)
        self.board = libmetawear.mbl_mw_metawearboard_create(byref(self._btle_connection))
        self._firmware_version = libmetawear.mbl_mw_metawearboard_initialize(self.board, FnVoid(self._initialized))

        self._primary_services = self.requester.discover_primary()

    def __str__(self):
        return "MetaWearClient, {0}".format(self._address)

    def __repr__(self):
        return "<MetaWearClient, {0}>".format(self._address)

    def _initialized(self):
        print("{0} initialized.".format(self))
        self.__initialized = True

    @property
    def requester(self):
        """Property handling `GattRequester` and its connection.

        :return: The connected GattRequester instance.
        :rtype: :class:`bluetooth.ble.GATTRequester`

        """
        if self._requester is None:
            if self._debug:
                print("Creating new GATTRequester...")
            self._requester = GATTRequester(self._address, False)

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

    def read_gatt_char(self, characteristic):
        """Read the desired data from the MetaWear board.

        :param pymetawear.mbientlab.metawear.core.GattCharacteristic characteristic: :class:`ctypes.POINTER`
            to a GattCharacteristic.
        :return: The read data.
        :rtype: str

        """
        uuid = self._characteristic_2_uuid(characteristic.contents)
        data = self.requester.read_by_uuid(str(uuid))[0]

        if self._debug:
            print("data received: {0}".format(data))
            print("bytes received: {0}".format(" ".join([hex(ord(b)) for b in data])))

        return data

    def write_gatt_char(self, characteristic, command, length):
        """Write the desired data to the MetaWear board.

        :param pymetawear.mbientlab.metawear.core.GattCharacteristic characteristic:
        :param POINTER command: The command to send, as a byte array pointer.
        :param int length: Length of the array that command points.
        :return:
        :rtype:

        """
        uuid = self._characteristic_2_uuid(characteristic.contents)
        # TODO: Find handle better. Is this even correct?
        q = self.requester.discover_characteristics(1, 65535, str(uuid))
        if len(q) > 1:
            raise PyMetaWearException("More than one characteristic matches.")
        else:
            q = q[0]

        data_to_send = self._command_to_str(command, length)
        return self.requester.write_by_handle(q.get('value_handle'), data_to_send)

    def _characteristic_2_uuid(self, characteristic):
        return uuid.UUID(int=(characteristic.uuid_high << 64) + characteristic.uuid_low)

    def _command_to_str(self, command, length):
        return str(bytearray([command[i] for i in xrange(length)]))

    def _sensor_data_handler(self, data):
        if (data.contents.type_id == DataTypeId.UINT32):
            data_ptr = cast(data.contents.value, POINTER(c_uint))
            return data_ptr.contents.value
        elif (data.contents.type_id == DataTypeId.FLOAT):
            data_ptr = cast(data.contents.value, POINTER(c_float))
            return data_ptr.contents.value
        elif (data.contents.type_id == DataTypeId.CARTESIAN_FLOAT):
            data_ptr = cast(data.contents.value, POINTER(CartesianFloat))
            return copy.deepcopy(data_ptr.contents)
        elif (data.contents.type_id == DataTypeId.BATTERY_STATE):
            data_ptr = cast(data.contents.value, POINTER(BatteryState))
            return copy.deepcopy(data_ptr.contents)
        elif (data.contents.type_id == DataTypeId.BYTE_ARRAY):
            data_ptr = cast(data.contents.value, POINTER(c_ubyte * data.contents.length))
            data_byte_array = []
            for i in range(0, data.contents.length):
                data_byte_array.append(data_ptr.contents[i])
            return data_byte_array
        elif (data.contents.type_id == DataTypeId.TCS34725_ADC):
            data_ptr = cast(data.contents.value, POINTER(Tcs34725ColorAdc))
            return copy.deepcopy(data_ptr.contents)

        else:
            raise RuntimeError('Unrecognized data type id: ' + str(data.contents.type_id))


if __name__ == '__main__':
    print("Discovering nearby MetaWear boards...")
    metawear_devices = discover_devices(timeout=2)
    if len(metawear_devices) < 1:
        pass
        raise ValueError("No MetaWear boards could be detected.")
    else:
        address = metawear_devices[0][0]

    c = MetaWearClient(address, debug=True)
    print("New client created: {0}".format(c))

    print("Blinking 10 times with green LED...")
    from pymetawear.mbientlab.metawear.peripheral import Led
    pattern = Led.Pattern(repeat_count=10)
    libmetawear.mbl_mw_led_load_preset_pattern(byref(pattern), Led.PRESET_BLINK)
    libmetawear.mbl_mw_led_write_pattern(c.board, byref(pattern), Led.COLOR_GREEN)
    libmetawear.mbl_mw_led_play(c.board)

    print("Reading battery state...")
    libmetawear.mbl_mw_settings_read_battery_state(c.board)
