#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Gyroscope module
----------------

Created by hbldh <henrik.blidh@nedomkull.com> on 2016-04-26

"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import re
import logging

from pymetawear import libmetawear
from pymetawear.exceptions import PyMetaWearException
from mbientlab.metawear.cbindings import GyroBmi160Odr, GyroBmi160Range
from pymetawear.modules.base import PyMetaWearLoggingModule, Modules, data_handler

log = logging.getLogger(__name__)


def require_bmi160(f):
    def wrapper(*args, **kwargs):
        if getattr(args[0], 'gyro_r_class', None) is None:
            raise PyMetaWearException("There is not Gyroscope "
                                      "module of your MetaWear board!")
        return f(*args, **kwargs)

    return wrapper


class GyroscopeModule(PyMetaWearLoggingModule):
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

        self.odr = {}
        self.fsr = {}

        self.current_odr = 0
        self.current_fsr = 0

        if self.module_id == Modules.MBL_MW_MODULE_NA:
            # No gyroscope present!
            self.gyro_r_class = None
            self.gyro_o_class = None
        else:
            self.gyro_r_class = GyroBmi160Range
            self.gyro_o_class = GyroBmi160Odr

        if self.gyro_o_class is not None:
            # Parse possible output data rates for this gyroscope.
            for key, value in vars(self.gyro_o_class).items():
                if re.search('_([0-9]+)Hz', key) and key is not None:
                    self.odr.update({key[1:-2]: value})

        if self.gyro_r_class is not None:
            # Parse possible ranges for this gyroscope.
            for key, value in vars(self.gyro_r_class).items():
                if re.search('_([0-9]+)dps', key) and key is not None:
                    self.fsr.update({key[1:-3]: value})
            
        if debug:
            log.setLevel(logging.DEBUG)

    def __str__(self):
        return "{0} {1}: Data rates (Hz): {2}, Data ranges (dps): {3}".format(
            self.module_name, self.sensor_name,
            [float(k) for k in sorted(self.odr.keys(),
                                      key=lambda x: (float(x)))],
            [k for k in sorted(self.fsr.keys())])

    def __repr__(self):
        return str(self)

    @property
    def module_name(self):
        return "Gyroscope"

    @property
    def sensor_name(self):
        if self.gyro_r_class is not None:
            return self.gyro_r_class.__name__.replace(
                'Gyro', '').replace('Range', '')
        else:
            return ''

    @property
    @require_bmi160
    def data_signal(self):
        if self.high_frequency_stream:
            return libmetawear.mbl_mw_gyro_bmi160_get_high_freq_rotation_data_signal(
                self.board)
        else:
            return libmetawear.mbl_mw_gyro_bmi160_get_rotation_data_signal(
                self.board)

    def _get_odr(self, value):
        sorted_ord_keys = sorted(self.odr.keys(), key=lambda x: (float(x)))
        diffs = [abs(value - float(k)) for k in sorted_ord_keys]
        min_diffs = min(diffs)
        if min_diffs > 0.5:
            raise ValueError(
                "Requested ODR ({0}) was not part of possible values: {1}".format(
                    value, [float(x) for x in sorted_ord_keys]))
        k = sorted_ord_keys[diffs.index(min_diffs)]
        return self.odr.get(k)

    def _get_fsr(self, value):
        sorted_ord_keys = sorted(self.fsr.keys(), key=lambda x: (float(x)))
        diffs = [abs(value - float(k)) for k in sorted_ord_keys]
        min_diffs = min(diffs)
        if min_diffs > 0.1:
            raise ValueError(
                "Requested FSR ({0}) was not part of possible values: {1}".format(
                    value, [float(x) for x in sorted(self.fsr.keys())]))
        k = sorted_ord_keys[diffs.index(min_diffs)]
        return self.fsr.get(k)

    @require_bmi160
    def get_current_settings(self):
        return "data_rate in Hz: {} data_range in deg/sec: {}".format(
            self.current_odr, self.current_fsr)

    @require_bmi160
    def get_possible_settings(self):
        return {
            'data_rate': [float(x) for x in sorted(
                self.odr.keys(), key=lambda x: (float(x)))],
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
                log.debug("Setting Gyroscope ODR to {0}".format(odr))
            libmetawear.mbl_mw_gyro_bmi160_set_odr(self.board, odr)
            self.current_odr = data_rate
        if data_range is not None:
            fsr = self._get_fsr(data_range)
            if self._debug:
                log.debug("Setting Gyroscope FSR to {0}".format(fsr))
            libmetawear.mbl_mw_gyro_bmi160_set_range(self.board, fsr)
            self.current_fsr = data_range
        if (data_rate is not None) or (data_range is not None):
            libmetawear.mbl_mw_gyro_bmi160_write_config(self.board)

    @require_bmi160
    def notifications(self, callback=None):
        """Subscribe or unsubscribe to gyroscope notifications.

        Convenience method for handling gyroscope usage.

        Example:

        .. code-block:: python

            def handle_notification(data):
                # Handle dictionary with [epoch, value] keys.
                epoch = data["epoch"]
                xyz = data["value"]
                print(str(data))

            mwclient.gyroscope.notifications(handle_notification)

        :param callable callback: Gyroscope notification callback function.
            If `None`, unsubscription to gyroscope notifications is registered.

        """
        if callback is None:
            self.stop()
            self.toggle_sampling(False)
            super(GyroscopeModule, self).notifications(None)
        else:
            super(GyroscopeModule, self).notifications(data_handler(callback))
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
