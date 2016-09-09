#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""

.. moduleauthor:: hbldh <henrik.blidh@nedomkull.com>

Created on 2016-04-26

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
from pymetawear.modules.base import PyMetaWearModule, Modules


def require_bmi160(f):
    def wrapper(*args, **kwargs):
        if getattr(args[0], 'gyro_class', None) is None:
            raise PyMetaWearException("There is not Gyroscope "
                                      "module of your MetaWear board!")
        return f(*args, **kwargs)
    return wrapper


class GyroscopeModule(PyMetaWearModule):
    """MetaWear gyroscope module implementation.

    :param ctypes.c_long board: The MetaWear board pointer value.
    :param int module_id: The module id of this gyroscope
        component, obtained from ``libmetawear``.
    :param bool debug: If ``True``, module prints out debug information.

    """

    def __init__(self, board, module_id, debug=False):
        super(GyroscopeModule, self).__init__(board, debug)
        self.module_id = module_id

        self.high_frequency_stream = False

        if self.module_id == Modules.MBL_MW_MODULE_NA:
            # No gyroscope present!
            self.gyro_class = None
        else:
            self.gyro_class = sensor.GyroBmi160

        if self.gyro_class is not None:
            # Parse possible output data rates for this accelerometer.
            self.odr = {int(re.search('^ODR_([0-9]+)HZ', k).groups()[0]):
                            getattr(self.gyro_class, k, None) for k in filter(
                lambda x: x.startswith('ODR'), vars(self.gyro_class))}
            self.fsr = {int(re.search('^FSR_([0-9]+)DPS', k).groups()[0]):
                            getattr(self.gyro_class, k, None) for k in
                        filter(lambda x: x.startswith('FSR'),
                               vars(self.gyro_class))}

    def __str__(self):
        return "{0} {1}: Data rates (Hz): {2}, Data ranges (dps): {3}".format(
            self.module_name, self.sensor_name,
            [float(k) for k in sorted(self.odr.keys(),
                                      key=lambda x:(float(x)))],
            [k for k in sorted(self.fsr.keys())])

    def __repr__(self):
        return str(self)

    @property
    def module_name(self):
        return "Gyroscope"

    @property
    def sensor_name(self):
        if self.gyro_class is not None:
            return self.gyro_class.__name__.replace('Gyro', '')
        else:
            return ''

    @property
    @require_bmi160
    def data_signal(self):
        if self.high_frequency_stream:
            return self._data_signal_preprocess(
                libmetawear.mbl_mw_gyro_bmi160_get_high_freq_rotation_data_signal)
        else:
            return self._data_signal_preprocess(
                libmetawear.mbl_mw_gyro_bmi160_get_rotation_data_signal)

    def _get_odr(self, value):
        sorted_ord_keys = sorted(self.odr.keys(), key=lambda x:(float(x)))
        diffs = [abs(value - float(k)) for k in sorted_ord_keys]
        min_diffs = min(diffs)
        if min_diffs > 0.5:
            raise ValueError("Requested ODR ({0}) was not part of "
                             "possible values: {1}".format(
                value, [float(x) for x in sorted_ord_keys]))
        k = int(sorted_ord_keys[diffs.index(min_diffs)])
        return self.odr.get(k)

    def _get_fsr(self, value):
        sorted_ord_keys = sorted(self.fsr.keys(), key=lambda x:(float(x)))
        diffs = [abs(value - float(k)) for k in sorted_ord_keys]
        min_diffs = min(diffs)
        if min_diffs > 0.1:
            raise ValueError("Requested FSR ({0}) was not part of "
                             "possible values: {1}".format(
                value, [float(x) for x in sorted(self.fsr.keys())]))
        k = int(sorted_ord_keys[diffs.index(min_diffs)])
        return self.fsr.get(k)

    @require_bmi160
    def get_current_settings(self):
        raise NotImplementedError()

    @require_bmi160
    def get_possible_settings(self):
        return {
            'data_rate': [float(x) for x in sorted(
                self.odr.keys(), key=lambda x:(float(x)))],
            'data_range': [x for x in sorted(self.fsr.keys())]
        }

    @require_bmi160
    def set_settings(self, data_rate=None, data_range=None):
        """Set gyroscope settings.

         Can be called with two or only one setting:

         .. code-block:: python

            mwclient.gyroscope.set_settings(data_rate=200.0, data_range=8.0)

        will give the same result as

        .. code-block:: python

            mwclient.gyroscope.set_settings(data_rate=200.0)
            mwclient.gyroscope.set_settings(data_range=1000.0)

        albeit that the latter example makes two writes to the board.

        Call :meth:`~get_possible_settings` to see which values
        that can be set for this sensor.

        :param float data_rate: The frequency of gyroscope updates in Hz.
        :param float data_range: The measurement range in the unit ``dps``,
            degrees per second.

        """
        if data_rate is not None:
            odr = self._get_odr(data_rate)
            if self._debug:
                print("Setting Gyroscope ODR to {0}".format(odr))
            libmetawear.mbl_mw_gyro_bmi160_set_odr(self.board, odr)
        if data_range is not None:
            fsr = self._get_fsr(data_range)
            if self._debug:
                print("Setting Gyroscope FSR to {0}".format(fsr))
            libmetawear.mbl_mw_gyro_bmi160_set_range(self.board, fsr)

        if (data_rate is not None) or (data_range is not None):
            libmetawear.mbl_mw_gyro_bmi160_write_config(self.board)

    @require_bmi160
    def notifications(self, callback=None):
        """Subscribe or unsubscribe to gyroscope notifications.

        Convenience method for handling gyroscope usage.

        Example:

        .. code-block:: python

            def handle_notification(data):
                # Handle a (epoch_time, (x,y,z)) gyroscope tuple.
                epoch = data[0]
                xyz = data[1]
                print("[{0}] X: {1}, Y: {2}, Z: {3}".format(epoch, *xyz))

            mwclient.gyroscope.notifications(handle_notification)

        :param callable callback: Gyroscope notification callback function.
            If `None`, unsubscription to gyroscope notifications is registered.

        """
        if callback is None:
            self.stop()
            self.toggle_sampling(False)
            super(GyroscopeModule, self).notifications(None)
        else:
            super(GyroscopeModule, self).notifications(
                sensor_data(callback))
            self.toggle_sampling(True)
            self.start()

    @require_bmi160
    def start(self):
        """Switches the gyroscope to active mode."""
        libmetawear.mbl_mw_gyro_bmi160_start(self.board)

    @require_bmi160
    def stop(self):
        """Switches the gyroscope to standby mode."""
        libmetawear.mbl_mw_gyro_bmi160_stop(self.board)

    @require_bmi160
    def toggle_sampling(self, enabled=True):
        """Enables or disables gyroscope sampling.

        :param bool enabled: Desired state of the gyroscope.

        """
        if enabled:
            libmetawear.mbl_mw_gyro_bmi160_enable_rotation_sampling(self.board)
        else:
            libmetawear.mbl_mw_gyro_bmi160_disable_rotation_sampling(self.board)


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
