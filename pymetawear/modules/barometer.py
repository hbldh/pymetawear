#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Barometer module
----------------

Created by hbldh <henrik.blidh@nedomkull.com> on 2016-08-16
Modified by lkasso <hello@mbientlab.com>

"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import re
import logging

from pymetawear import libmetawear
from mbientlab.metawear.cbindings import BaroBme280StandbyTime, \
    BaroBmp280StandbyTime, BaroBoschIirFilter, \
    BaroBoschOversampling
from pymetawear.modules.base import PyMetaWearModule, data_handler

log = logging.getLogger(__name__)


class BarometerModule(PyMetaWearModule):
    """MetaWear barometer module implementation.

    :param ctypes.c_long board: The MetaWear board pointer value.
    :param int module_id: The module id of this barometer
        component, obtained from ``libmetawear``.
    :param bool debug: If ``True``, module prints out debug information.

    """

    def __init__(self, board, module_id, debug=False):
        super(BarometerModule, self).__init__(board, debug)
        self.module_id = module_id
        self._altitude_data = True

        self.oversampling = {}
        self.iir_filter = {}
        self.standby_time = {}

        self.current_oversampling = 0
        self.current_iir_filter = 0
        self.current_standby_time = 0

        barometer_standbytime_sensors = {
            0: BaroBmp280StandbyTime,
            1: BaroBme280StandbyTime,
        }
        self.barometer_o_class = BaroBoschOversampling
        self.barometer_i_class = BaroBoschIirFilter
        self.barometer_s_class = barometer_standbytime_sensors.get(
            self.module_id, None)

        if self.barometer_o_class is not None:
            # Parse oversampling status
            for key, value in vars(self.barometer_o_class).items():
                if re.search('^([A-Z_]*)', key) and isinstance(value, int):
                    self.oversampling.update({key.lower():value})

        if self.barometer_i_class is not None:
            # Parse IR filter values 
            for key, value in vars(self.barometer_i_class).items():
                if re.search('^AVG_([0-9]+)', key) and isinstance(value, int):
                    self.iir_filter.update({key.lower():value})
                elif key == 'OFF':
                    self.iir_filter.update({'off': isinstance(value, int)})

        if self.barometer_s_class is not None:
            # Parse standby time values 
            for key, value in vars(self.barometer_s_class).items():
                if re.search('^_([0-9]+)_*([0-9]*)ms', key) and isinstance(value, int):
                    self.standby_time.update({key[1:-2].replace("_",".").lower():value})
            
        else:
            self.is_present = False

        if debug:
            log.setLevel(logging.DEBUG)

    def __str__(self):
        return "{0} {1}".format(
            self.module_name, self.sensor_name)

    def __repr__(self):
        return str(self)

    def set_altitude_data(self, status=True):
        """Change between altitude and pressure output.

        :param bool status:

        """
        self._altitude_data = bool(status)

    @property
    def module_name(self):
        return "Barometer"

    @property
    def sensor_name(self):
        return self.barometer_s_class.__name__.replace('Baro', '').replace('StandbyTime', '')

    @property
    def data_signal(self):
        if self._altitude_data:
            return libmetawear.mbl_mw_baro_bosch_get_altitude_data_signal(
                self.board)
        else:
            return libmetawear.mbl_mw_baro_bosch_get_pressure_data_signal(
                self.board)

    def _get_oversampling(self, value):
        if value.lower() in self.oversampling:
            return self.oversampling.get(value.lower())
        else:
            raise ValueError(
                "Requested oversampling ({0}) was not part of possible values: {1}".format(
                    value.lower(), self.oversampling.keys()))

    def _get_iir_filter(self, value):
        if value.lower() in self.iir_filter:
            return self.iir_filter.get(value.lower())
        else:
            raise ValueError(
                "Requested IIR filter ({0}) was not part of possible values: {1}".format(
                    value.lower(), self.iir_filter.keys()))

    def _get_standby_time(self, value):
        sorted_ord_keys = sorted(self.standby_time.keys(),
                                 key=lambda x: (float(x)))
        diffs = [abs(value - float(k)) for k in sorted_ord_keys]
        min_diffs = min(diffs)
        if min_diffs > 0.5:
            raise ValueError(
                "Requested standby time ({0}) was not part of possible values: {1}".format(
                    value, [float(x) for x in sorted_ord_keys]))
        return float(value)

    def get_current_settings(self):
        return "oversampling variables: {} IR filter average: {} standby time in ms: {}".format(self.current_oversampling, self.current_iir_filter, self.current_standby_time)  

    def get_possible_settings(self):
        return {
            'oversampling': [x.lower() for x in sorted(
                self.oversampling.keys(), key=lambda x: (x.lower()))],
            'iir_filter': [x.lower() for x in sorted(
                self.iir_filter.keys(), key=lambda x: (x.lower()))],
            'standby_time': [float(x) for x in sorted(
                self.standby_time.keys(), key=lambda x: (float(x)))],
        }

    def set_settings(self, oversampling=None, iir_filter=None,
                     standby_time=None):
        """Set barometer settings.

         Can be called with 1-3 setting:

         .. code-block:: python

            mwclient.set_settings(oversampling='low_power',
                                  iir_filter='avg_2',
                                  standby_time=125.0)

        will give the same result as

        .. code-block:: python

            mwclient.set_settings(oversampling='low_power')
            mwclient.set_settings(iir_filter='avg_2')
            mwclient.set_settings(standby_time=125.0)

        albeit that the latter example makes two writes to the board.

        Call :meth:`~get_possible_settings` to see which values
        that can be set for this sensor.

        :param str oversampling:
        :param str iir_filter:
        :param float standby_time:

        """
        if oversampling is not None:
            oversampling = self._get_oversampling(oversampling)
            if self._debug:
                log.debug("Setting Barometer Oversampling to {0}".format(
                    oversampling))
            libmetawear.mbl_mw_baro_bosch_set_oversampling(
                self.board, oversampling)
            self.current_oversampling = oversampling

        if iir_filter is not None:
            iir_filter = self._get_iir_filter(iir_filter)
            if self._debug:
                log.debug(
                    "Setting Barometer IIR filter to {0}".format(iir_filter))
            libmetawear.mbl_mw_baro_bosch_set_iir_filter(
                self.board, iir_filter)
            self.current_iir_filter = iir_filter

        if standby_time is not None:
            standby_time = self._get_standby_time(standby_time)
            if self._debug:
                log.debug("Setting Barometer Standby Time to {0}".format(
                    standby_time))
            libmetawear.mbl_mw_baro_bosch_set_standby_time(
                self.board, standby_time)
            self.current_standby_time = standby_time

        if (oversampling is not None) or (iir_filter is not None) or \
                (standby_time is not None):
            libmetawear.mbl_mw_baro_bosch_write_config(self.board)

    def notifications(self, callback=None):
        """Subscribe to or unsubscribe from barometer notifications.

        Convenience method for handling barometer usage.

        Example:

        .. code-block:: python

            def handle_barometer_notification(data)
                # Handle dictionary with [epoch, value] keys.
                epoch = data["epoch"]
                value = data["value"]
                print(data)

            mwclient.barometer.notifications(handle_barometer_notification)

        :param callable callback: Barometer notification callback function.
            If `None`, unsubscription to barometer notifications is registered.

        """

        if callback is None:
            self.stop()
            super(BarometerModule, self).notifications(None)
        else:
            super(BarometerModule, self).notifications(data_handler(callback))
            self.start()

    def start(self):
        """Switches the barometer to active mode."""
        libmetawear.mbl_mw_baro_bosch_start(self.board)

    def stop(self):
        """Switches the barometer to standby mode."""
        libmetawear.mbl_mw_baro_bosch_stop(self.board)
