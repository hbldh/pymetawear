#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""

.. moduleauthor:: hbldh <henrik.blidh@nedomkull.com>

Created: 2016-04-14

"""

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import

import re
from functools import wraps
from ctypes import c_float, cast, POINTER

from pymetawear import libmetawear
from pymetawear.exceptions import PyMetaWearException
from pymetawear.mbientlab.metawear import sensor
from pymetawear.mbientlab.metawear.core import DataTypeId, CartesianFloat
from pymetawear.modules.base import PyMetaWearModule


class AccelerometerModule(PyMetaWearModule):
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
            self.fsr = {float(re.search('^FSR_([0-9]+)G', k).groups()[0]):
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
        if self.high_frequency_stream:
            return self._data_signal_preprocess(
                libmetawear.mbl_mw_acc_get_high_freq_acceleration_data_signal)
        else:
            return self._data_signal_preprocess(
                libmetawear.mbl_mw_acc_get_acceleration_data_signal)

    def _get_odr(self, value):
        sorted_ord_keys = sorted(self.odr.keys(), key=lambda x:(float(x)))
        diffs = [abs(value - float(k)) for k in sorted_ord_keys]
        min_diffs = min(diffs)
        if min_diffs > 0.5:
            raise ValueError("Requested ODR ({0}) was not part of "
                             "possible values: {1}".format(
                value, [float(x) for x in sorted_ord_keys]))
        return float(value)

    def _get_fsr(self, value):
        sorted_ord_keys = sorted(self.fsr.keys(), key=lambda x:(float(x)))
        diffs = [abs(value - float(k)) for k in sorted_ord_keys]
        min_diffs = min(diffs)
        if min_diffs > 0.1:
            raise ValueError("Requested FSR ({0}) was not part of "
                             "possible values: {1}".format(
                value, [x for x in sorted(self.fsr.keys())]))
        return float(value)

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

        Call :meth:`~get_possible_settings` to see which values
        that can be set for this sensor.

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

    def notifications(self, callback=None):
        """Subscribe or unsubscribe to accelerometer notifications.

        Convenience method for handling accelerometer usage.

        Example:

        .. code-block:: python

            def handle_acc_notification(data)
                # Handle a (epoch_time, (x,y,z)) accelerometer tuple.
                epoch = data[0]
                xyz = data[1]
                print("[{0}] X: {1}, Y: {2}, Z: {3}".format(epoch, *xyz))

            mwclient.accelerometer.notifications(handle_acc_notification)

        :param callable callback: Accelerometer notification callback function.
            If `None`, unsubscription to accelerometer notifications is registered.

        """

        if callback is None:
            self.stop()
            self.toggle_sampling(False)
            super(AccelerometerModule, self).notifications(None)
        else:
            super(AccelerometerModule, self).notifications(
                sensor_data(callback))
            self.toggle_sampling(True)
            self.start()

    def start(self):
        """Switches the accelerometer to active mode."""
        libmetawear.mbl_mw_acc_start(self.board)

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


def sensor_data(func):
    @wraps(func)
    def wrapper(data):
        if data.contents.type_id == DataTypeId.CARTESIAN_FLOAT:
            epoch = int(data.contents.epoch)
            data_ptr = cast(data.contents.value, POINTER(CartesianFloat))
            func((epoch, (data_ptr.contents.x,
                          data_ptr.contents.y,
                          data_ptr.contents.z)))
        else:
            raise PyMetaWearException('Incorrect data type id: {0}'.format(
                data.contents.type_id))
    return wrapper
