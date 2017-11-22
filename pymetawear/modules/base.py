#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Base module
-----------

Created by hbldh <henrik.blidh@nedomkull.com> on 2016-04-14
Modified by lkasso <hello@mbientlab.com>

"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import logging
from ctypes import c_int, c_uint, c_float, cast, POINTER, c_ubyte
from functools import wraps

from pymetawear import libmetawear
from pymetawear.exceptions import PyMetaWearException
from mbientlab.metawear.cbindings import FnVoid_DataP, DataTypeId, \
    CartesianFloat, BatteryState, Tcs34725ColorAdc, EulerAngles, \
    Quaternion, CorrectedCartesianFloat

log = logging.getLogger(__name__)


class Modules(object):
    """Class for storing PyMetaWear module identifiers."""

    MBL_MW_MODULE_NA = -1
    MBL_MW_MODULE_SWITCH = 1
    MBL_MW_MODULE_LED = 2
    MBL_MW_MODULE_ACCELEROMETER = 3
    MBL_MW_MODULE_TEMPERATURE = 4
    MBL_MW_MODULE_GPIO = 5
    MBL_MW_MODULE_NEO_PIXEL = 6
    MBL_MW_MODULE_IBEACON = 7
    MBL_MW_MODULE_HAPTIC = 8
    MBL_MW_MODULE_DATA_PROCESSOR = 9
    MBL_MW_MODULE_EVENT = 0xa
    MBL_MW_MODULE_LOGGING = 0xb
    MBL_MW_MODULE_TIMER = 0xc
    MBL_MW_MODULE_I2C = 0xd
    MBL_MW_MODULE_MACRO = 0xf
    MBL_MW_MODULE_GSR = 0x10
    MBL_MW_MODULE_SETTINGS = 0x11
    MBL_MW_MODULE_BAROMETER = 0x12
    MBL_MW_MODULE_GYRO = 0x13
    MBL_MW_MODULE_AMBIENT_LIGHT = 0x14
    MBL_MW_MODULE_MAGNETOMETER = 0x15
    MBL_MW_MODULE_HUMIDITY = 0x16
    MBL_MW_MODULE_COLOR_DETECTOR = 0x17
    MBL_MW_MODULE_PROXIMITY = 0x18
    MBL_MW_MODULE_SENSOR_FUSION = 0x19
    MBL_MW_MODULE_DEBUG = 0xfe


class PyMetaWearModule(object):
    """Base class for PyMetaWear module implementations.

    :param ctypes.c_long board: The MetaWear board pointer value.
    :param bool debug: If ``True``, module prints out debug information.

    """

    def __init__(self, board, debug=False):
        self.board = board
        self._debug = debug
        self.is_present = True
        self.callback = None

        if debug:
            log.setLevel(logging.DEBUG)

    def __str__(self):
        return "PyMetaWearModule"

    def __repr__(self):
        return super(PyMetaWearModule, self).__repr__()

    @property
    def module_name(self):
        """Get module name.

        :return: The name of this module.
        :rtype: str

        """
        return ''

    @property
    def sensor_name(self):
        """Get sensor name, if applicable.

        :return: The name of this module.
        :rtype: str or None

        """
        return None

    @property
    def data_signal(self):
        """Returns the data signal pointer value for the switch module.

        :returns: The pointer value. (Long if on x64 architecture.)
        :rtype: :py:class:`ctypes.c_long` or :py:class:`ctypes.c_int`

        """
        raise PyMetaWearException(
            "No data signal exists for {0} module.".format(self))

    def set_settings(self, **kwargs):
        raise PyMetaWearException(
            "No settings exists for {0} module.".format(self))

    def get_current_settings(self):
        return {}

    def get_possible_settings(self):
        return {}

    def notifications(self, callback=None):
        """Toggle notifications/subscriptions to data signals
        on the MetaWear board.

        :param callable callback: The function to call when
            data signal notification arrives. If ``None``, an
            unsubscription to notifications is sent.

        """
        data_signal = self.data_signal
        if callback is not None:
            if self._debug:
                log.debug("Subscribing to {0} changes. (Sig#: {1})".format(
                    self.module_name, data_signal))
            if self.callback is not None:
                raise PyMetaWearException(
                    "Subscription to {0} signal already in place!")
            self.callback = (callback, FnVoid_DataP(callback))
            libmetawear.mbl_mw_datasignal_subscribe(
                data_signal, self.callback[1])
        else:
            if self._debug:
                log.debug("Unsubscribing to {0} changes. (Sig#: {1})".format(
                    self.module_name, data_signal))
            if self.callback is None:
                return
            libmetawear.mbl_mw_datasignal_unsubscribe(data_signal)
            self.callback = None


def _error_handler(data):
    raise RuntimeError('Unrecognized data type id: ' +
                       str(data.contents.type_id))


def _byte_array_handler(data):
    ptr = cast(data.contents.value, POINTER(c_ubyte * data.contents.length))
    return [ptr.contents[i].value for i in range(0, data.contents.length)]


DATA_HANDLERS = {
    DataTypeId.UINT32: lambda x: cast(
        x.contents.value, POINTER(c_uint)).contents.value,
    DataTypeId.INT32: lambda x: cast(
        x.contents.value, POINTER(c_int)).contents.value,
    DataTypeId.FLOAT: lambda x: cast(
        x.contents.value, POINTER(c_float)).contents.value,
    DataTypeId.CARTESIAN_FLOAT: lambda x: cast(
        x.contents.value, POINTER(CartesianFloat)).contents,
    DataTypeId.BATTERY_STATE: lambda x: cast(
        x.contents.value, POINTER(BatteryState)).contents,
    DataTypeId.BYTE_ARRAY: _byte_array_handler,
    DataTypeId.TCS34725_ADC: lambda x: cast(
        x.contents.value, POINTER(Tcs34725ColorAdc)).contents,
    DataTypeId.EULER_ANGLE: lambda x: cast(
        x.contents.value, POINTER(EulerAngles)).contents,
    DataTypeId.QUATERNION: lambda x: cast(
        x.contents.value, POINTER(Quaternion)).contents,
    DataTypeId.CORRECTED_CARTESIAN_FLOAT: lambda x: cast(
        x.contents.value, POINTER(CorrectedCartesianFloat)).contents
}


def data_handler(func):
    @wraps(func)
    def wrapper(data):
        func({
            'epoch': int(data.contents.epoch),
            'value': DATA_HANDLERS.get(
                data.contents.type_id, _error_handler)(data)
        })
    return wrapper
