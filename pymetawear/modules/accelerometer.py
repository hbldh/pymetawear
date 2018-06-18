#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Accelerometer module
--------------------

Created by hbldh <henrik.blidh@nedomkull.com> on 2016-04-14
Modified by lkasso <hello@mbientlab.com>

"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import re
import logging
from ctypes import c_float

from pymetawear import libmetawear
from mbientlab.metawear.cbindings import AccBma255Odr, AccBmi160Odr, \
    AccBmi160StepCounterMode, AccBoschOrientationMode, AccBoschRange, \
    AccMma8452qOdr, AccMma8452qRange, Const
from pymetawear.modules.base import PyMetaWearLoggingModule, data_handler

log = logging.getLogger(__name__)

_settings_map = {
    Const.MODULE_ACC_TYPE_BMA255: (AccBma255Odr, AccBoschRange),
    Const.MODULE_ACC_TYPE_BMI160: (AccBmi160Odr, AccBoschRange),
    Const.MODULE_ACC_TYPE_MMA8452Q: (AccMma8452qOdr, AccMma8452qRange)
}


class AccelerometerModule(PyMetaWearLoggingModule):
    """MetaWear accelerometer module implementation.

    :param ctypes.c_long board: The MetaWear board pointer value.
    :param int module_id: The module id of this accelerometer
        component, obtained from ``libmetawear``.
    :param bool debug: If ``True``, module prints out debug information.

    """

    def __init__(self, board, module_id, debug=False):
        super(AccelerometerModule, self).__init__(board, debug)
        self.module_id = module_id

        self.high_frequency_stream = False

        self.current_odr = 0
        self.current_fsr = 0

        self.odr = {}
        self.fsr = {}

        acc_odr_class, acc_fsr_class = _settings_map.get(module_id)

        if acc_odr_class is not None:
            # Parse possible output data rates for this accelerometer.
            for key, value in vars(acc_odr_class).items():
                if re.search('^_([0-9]+)_*([0-9]*)Hz', key) and key is not None:
                    self.odr.update({key[1:-2].replace("_","."): value})

        if acc_fsr_class is not None:
            # Parse possible output data ranges for this accelerometer.
            for key, value in vars(acc_fsr_class).items():
                if re.search('^_([0-9]+)G', key) and key is not None:
                    self.fsr.update({key[1:-1]: value})

        self._acc_sensor_name = acc_odr_class.__name__.replace(
            'Acc', '').replace('Odr', '')
        if debug:
            log.setLevel(logging.DEBUG)

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
        return self._acc_sensor_name

    @property
    def data_signal(self):
        if self.high_frequency_stream:
            return libmetawear.mbl_mw_acc_get_high_freq_acceleration_data_signal(self.board)
        else:
            return libmetawear.mbl_mw_acc_get_acceleration_data_signal(self.board)

    def _get_odr(self, value):
        sorted_ord_keys = sorted(self.odr.keys(), key=lambda x: (float(x)))
        diffs = [abs(value - float(k)) for k in sorted_ord_keys]
        min_diffs = min(diffs)
        if min_diffs > 0.5:
            raise ValueError(
                "Requested ODR ({0}) was not part of possible values: {1}".format(
                    value, [float(x) for x in sorted_ord_keys]))
        return float(value)

    def _get_fsr(self, value):
        sorted_ord_keys = sorted(self.fsr.keys(), key=lambda x: (float(x)))
        diffs = [abs(value - float(k)) for k in sorted_ord_keys]
        min_diffs = min(diffs)
        if min_diffs > 0.1:
            raise ValueError(
                "Requested FSR ({0}) was not part of possible values: {1}".format(
                    value, [x for x in sorted(self.fsr.keys())]))
        return float(value)

    def get_current_settings(self):
        return "data_rate in Hz: {} data_range in Gs: {}".format(
            self.current_odr, self.current_fsr)

    def get_possible_settings(self):
        return {
            'data_rate in Hz': [float(x) for x in sorted(
                self.odr.keys(), key=lambda x:(float(x)))],
            'data_range in Gs': [int(x) for x in sorted(self.fsr.keys())]
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

        Call :meth:`~get_possible_settings` to see which values
        that can be set for this sensor.

        :param float data_rate: The frequency of accelerometer updates in Hz.
        :param float data_range: The measurement range in the unit ``g``.

        """

        if data_rate is not None:
            self.current_odr = data_rate
            odr = self._get_odr(data_rate)
            if self._debug:
                log.debug("Setting Accelerometer ODR to {0}".format(odr))
            libmetawear.mbl_mw_acc_set_odr(self.board, c_float(odr))
       
        if data_range is not None:
            self.current_fsr = data_range
            fsr = self._get_fsr(data_range)
            if self._debug:
                log.debug("Setting Accelerometer FSR to {0}".format(fsr))
            libmetawear.mbl_mw_acc_set_range(self.board, c_float(fsr))

        if (data_rate is not None) or (data_range is not None):
            self.current_odr = data_rate
            self.current_fsr = data_range
            libmetawear.mbl_mw_acc_write_acceleration_config(self.board)

    def notifications(self, callback=None):
        """Subscribe or unsubscribe to accelerometer notifications.

        Convenience method for handling accelerometer usage.

        Example:

        .. code-block:: python

            def handle_acc_notification(data)
                # Handle dictionary with [epoch, value] keys.
                epoch = data["epoch"]
                xyz = data["value"]
                print(str(data))

            mwclient.accelerometer.notifications(handle_acc_notification)

        :param callable callback: Accelerometer notification callback function.
            If `None`, unsubscription to accelerometer notifications
            is registered.

        """

        if callback is None:
            self.stop()
            self.toggle_sampling(False)
            super(AccelerometerModule, self).notifications(None)
        else:
            super(AccelerometerModule, self).notifications(
                data_handler(callback))
            self.toggle_sampling(True)
            self.start()

    def start(self):
        """Switches the accelerometer to active mode."""
        libmetawear.mbl_mw_acc_start(self.board)
        if self._debug:
            log.debug("Start Sampling (Accelerometer)")

    def stop(self):
        """Switches the accelerometer to standby mode."""
        libmetawear.mbl_mw_acc_stop(self.board)

    def toggle_sampling(self, enabled=True):
        """Enables or disables accelerometer sampling.

        :param bool enabled: Desired state of the accelerometer.

        """
        if enabled:
            libmetawear.mbl_mw_acc_enable_acceleration_sampling(self.board)
        else:
            libmetawear.mbl_mw_acc_disable_acceleration_sampling(self.board)
