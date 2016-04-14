#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:mod:`accelerometer`
==================

Created by hbldh <henrik.blidh@nedomkull.com>
Created on 2016-04-14

"""

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import

import re

from ctypes import c_float

from pymetawear import libmetawear
from pymetawear.mbientlab.metawear import sensor
from pymetawear.modules.base import PyMetaWearModule


class PyMetaWearAccelerometer(PyMetaWearModule):

    def __init__(self, board, module_id, debug=False):
        super(PyMetaWearAccelerometer, self).__init__(board, debug)
        self.module_id = module_id

        acc_sensors = [
            sensor.AccelerometerBmi160,
            sensor.AccelerometerBma255,
            sensor.AccelerometerMma8452q
        ]
        for a in acc_sensors:
            if getattr(a, 'MODULE_TYPE', -1) == module_id:
                self.acc_class = a

        if self.acc_class is not None:
            # Parse possible output data rates for this accelerometer.
            self.odr = {".".join(re.search(
                '^ODR_([0-9]+)\_*([0-9]*)HZ', k).groups()):
                            getattr(self.acc_class, k, None) for k in filter(
                lambda x: x.startswith('ODR'), vars(self.acc_class))}

            # Parse possible output data ranges for this accelerometer.
            if len(list(filter(lambda x: x.startswith('FSR'),
                               vars(self.acc_class)))) == 0:
                acc_class = sensor.AccelerometerBosch
            else:
                acc_class = self.acc_class
            self.fsr = {int(re.search('^FSR_([0-9]+)G', k).groups()[0]):
                            getattr(acc_class, k, None) for k in
                        filter(lambda x: x.startswith('FSR'), vars(acc_class))}

    def __str__(self):
        return "{0} {1}: Data rates (Hz): {2}, Data ranges (g): {3}".format(
            self.module_name, self.sensor_name,
            [float(k) for k in sorted(self.odr.keys(),
                                      key=lambda x:(float(x)))],
            [k for k in sorted(self.fsr.keys())])

    def __repr__(self):
        return str(self)

    @property
    def module_name(self):
        return "Accelerometer"

    @property
    def sensor_name(self):
        return self.acc_class.__name__.replace('Accelerometer', '')

    @property
    def data_signal(self):
        return self._data_signal_preprocess(
            libmetawear.mbl_mw_acc_get_acceleration_data_signal)

    def get_settings(self):
        pass

    def _get_odr(self, value):
        sorted_ord_keys = sorted(self.odr.keys(), key=lambda x:(float(x)))
        diffs = [abs(value - float(k)) for k in sorted_ord_keys]
        min_diffs = min(diffs)
        if min_diffs > 0.5:
            raise ValueError("Requested ODR ({0}) was not part of "
                             "possible values: {1}".format(
                value, [float(x) for x in sorted_ord_keys]))
        return self.odr.get(sorted_ord_keys[diffs.index(min_diffs)])

    def _get_fsr(self, value):
        fsr = self.fsr.get(value, None)
        if fsr is None:
            raise ValueError("Requested FSR ({0}) was not part of "
                             "possible values: {1}".format(
                value, [x for x in sorted(self.fsr.keys())]))
        return float(fsr)

    def get_current_settings(self):
        raise NotImplementedError()

    def get_possible_settings(self):
        return {
            'data_rate': [float(x) for x in sorted(
                self.odr.keys(), key=lambda x:(float(x)))],
            'data_range': [x for x in sorted(self.fsr.keys())]
        }

    def set_settings(self, data_rate=None, data_range=None):
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
            odr = self._get_odr(data_rate)
            if self._debug:
                print("Setting Accelerometer ODR to {0}".format(odr))
            libmetawear.mbl_mw_acc_set_odr(self.board, c_float(odr))
        if data_range is not None:
            fsr = self._get_fsr(data_range)
            if self._debug:
                print("Setting Accelerometer FSR to {0}".format(fsr))
            libmetawear.mbl_mw_acc_set_range(self.board, c_float(fsr))

        if (data_rate is not None) or (data_range is not None):
            libmetawear.mbl_mw_acc_write_acceleration_config(self.board)
