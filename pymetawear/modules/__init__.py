#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:mod:`modules`
==================

Created by hbldh <henrik.blidh@nedomkull.com>
Created on 2016-04-14

"""

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import

from ctypes import c_long

from pymetawear import libmetawear
from pymetawear.utils import IS_64_BIT
from pymetawear.exceptions import PyMetaWearException
from pymetawear.mbientlab.metawear.core import FnDataPtr


class Modules(object):

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
    MBL_MW_MODULE_DEBUG = 0xfe


class PyMetaWearModule(object):

    def __init__(self, board, debug=False):
        self.board = board
        self._debug = debug

        self.callback = None

    def __str__(self):
        return "PyMetaWear module: {0}".format()

    def __repr__(self):
        return super(PyMetaWearModule, self).__repr__()

    @property
    def module_name(self):
        return ''

    @property
    def sensor_name(self):
        return ''

    @property
    def data_signal(self):
        raise NotImplementedError()

    def set_settings(self, **kwargs):
        raise NotImplementedError()

    def get_current_settings(self):
        raise NotImplementedError()

    def get_possible_settings(self):
        raise NotImplementedError()

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
                print("Subscribing to {0} changes. (Sig#: {1})".format(
                    self.module_name, data_signal))
            if self.callback is not None:
                raise PyMetaWearException(
                    "Subscription to {0} signal already in place!")
            self.callback = (callback, FnDataPtr(callback))
            libmetawear.mbl_mw_datasignal_subscribe(
                data_signal, self.callback[1])
        else:
            if self._debug:
                print("Unsubscribing to {0} changes. (Sig#: {1})".format(
                    self.module_name, data_signal))
            if self.callback is None:
                return
            libmetawear.mbl_mw_datasignal_unsubscribe(data_signal)
            self.callback = None

    def _data_signal_preprocess(self, data_signal_func):
        if IS_64_BIT:
            data_signal_func.restype = c_long
            data_signal = c_long(data_signal_func(self.board))
        else:
            data_signal = data_signal_func(self.board)
        return data_signal


