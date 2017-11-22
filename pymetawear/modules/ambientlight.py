#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Ambient Light module
--------------------

Created by hbldh <henrik.blidh@nedomkull.com> on 2016-04-28
Modified by lkasso <hello@mbientlab.com>

"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import re

import logging

from pymetawear import libmetawear
from pymetawear.exceptions import PyMetaWearException
from mbientlab.metawear.cbindings import AlsLtr329Gain, \
    AlsLtr329IntegrationTime, AlsLtr329MeasurementRate
from pymetawear.modules.base import PyMetaWearModule, Modules, data_handler

log = logging.getLogger(__name__)


def require_ltr329(f):
    def wrapper(*args, **kwargs):
        if getattr(args[0], 'ambient_light_gain_class', None) is None:
            raise PyMetaWearException("There is no Ambient Light "
                                      "module on your MetaWear board!")
        return f(*args, **kwargs)
    return wrapper


class AmbientLightModule(PyMetaWearModule):
    """MetaWear Ambient Light module implementation.

    :param ctypes.c_long board: The MetaWear board pointer value.
    :param bool debug: If ``True``, module prints out debug information.

    """

    def __init__(self, board, module_id, debug=False):
        super(AmbientLightModule, self).__init__(board, debug)
        self.module_id = module_id
        self.gain = {}
        self.integration_time = {}
        self.measurement_rate = {}

        if self.module_id == Modules.MBL_MW_MODULE_NA:
            # No ambient light sensor present!
            self.ambient_light_gain_class = None
            self.ambient_light_time_class = None
            self.ambient_light_rate_class = None
            self.is_present = False
        else:
            self.ambient_light_gain_class = AlsLtr329Gain
            self.ambient_light_time_class = AlsLtr329IntegrationTime
            self.ambient_light_rate_class = AlsLtr329MeasurementRate

        if self.ambient_light_gain_class is not None:
            # Parse possible gain rates for this light sensor.
            for key, value in vars(self.ambient_light_gain_class).items():
                if re.search('^_([0-9]+)X', key):
                    self.gain.update({key[1:-1]:value})

        if self.ambient_light_time_class is not None:
            # Parse possible integration time rates for this light sensor.
            for key, value in vars(self.ambient_light_time_class).items():
                if re.search('^_([0-9]+)ms', key):
                    self.integration_time.update({key[1:-2]:value})

        if self.ambient_light_rate_class is not None:
            # Parse possible measurement time rates for this light sensor.
            for key, value in vars(self.ambient_light_rate_class).items():
                if re.search('^_([0-9]+)ms', key):
                    self.measurement_rate.update({key[1:-2]:value})
           
        if debug:
            log.setLevel(logging.DEBUG)

    def __str__(self):
        return "{0}".format(
            self.module_name)

    def __repr__(self):
        return str(self)

    @property
    def module_name(self):
        return "Ambient Light"

    @property
    @require_ltr329
    def data_signal(self):
        return libmetawear.mbl_mw_als_ltr329_get_illuminance_data_signal(self.board)

    @require_ltr329
    def get_current_settings(self):
        raise NotImplementedError()

    @require_ltr329
    def get_possible_settings(self):
        return {
            'gain': [x for x in sorted(self.gain.keys())],
            'integration_time': [x for x in sorted(
                self.integration_time.keys())],
            'measurement_rate': [x for x in sorted(
                self.measurement_rate.keys())]
        }

    def _get_gain(self, value):
        sorted_ord_keys = sorted(self.gain.keys(),
                                 key=lambda x: (float(x)))
        diffs = [abs(value - float(k)) for k in sorted_ord_keys]
        min_diffs = min(diffs)
        if min_diffs > 0.5:
            raise ValueError(
                "Requested gain ({0}) was not part of possible values: {1}".format(
                    value, [float(x) for x in sorted_ord_keys]))
        #k = int(sorted_ord_keys[diffs.index(min_diffs)])
        k = sorted_ord_keys[diffs.index(min_diffs)]
        return self.gain.get(k)

    def _get_integration_time(self, value):
        sorted_ord_keys = sorted(self.integration_time.keys(),
                                 key=lambda x: (float(x)))
        diffs = [abs(value - float(k)) for k in sorted_ord_keys]
        min_diffs = min(diffs)
        if min_diffs > 0.5:
            raise ValueError(
                "Requested integration time ({0}) was not part of possible values: {1}".format(
                    value, [float(x) for x in sorted_ord_keys]))
        #k = int(sorted_ord_keys[diffs.index(min_diffs)])
        k = sorted_ord_keys[diffs.index(min_diffs)]
        return self.integration_time.get(k)

    def _get_measurement_rate(self, value):
        sorted_ord_keys = sorted(self.measurement_rate.keys(),
                                 key=lambda x: (float(x)))
        diffs = [abs(value - float(k)) for k in sorted_ord_keys]
        min_diffs = min(diffs)
        if min_diffs > 0.5:
            raise ValueError(
                "Requested measurement rate ({0}) was not part of possible values: {1}".format(
                    value, [float(x) for x in sorted_ord_keys]))
        #k = int(sorted_ord_keys[diffs.index(min_diffs)])
        k = sorted_ord_keys[diffs.index(min_diffs)]
        return self.measurement_rate.get(k)

    @require_ltr329
    def set_settings(self, gain=None, integration_time=None,
                     measurement_rate=None):
        """Set ambient light sensor settings.

         Can be called with two or only one setting:

         .. code-block:: python

            mwclient.ambient_light.set_settings(
                gain=4,
                integration_time=200,
                measurement_rate=200)

        will give the same result as

        .. code-block:: python

            mwclient.ambient_light.set_settings(gain=4)
            mwclient.ambient_light.set_settings(integration_time=200)
            mwclient.ambient_light.set_settings(measurement_rate=200)

        albeit that the latter example makes three writes to the board.

        Call :meth:`~get_possible_settings` to see which values
        that can be set for this sensor.

        :param float gain: Sensor gain
        :param float integration_time: Sensor integration time
        :param float measurement_rate: Sensor measurement rate

        """
        if gain is not None:
            g = self._get_gain(gain)
            if self._debug:
                log.debug("Setting Ambient Light gain to {0}".format(g))
            libmetawear.mbl_mw_als_ltr329_set_gain(self.board, g)
        if integration_time is not None:
            itime = self._get_integration_time(integration_time)
            if self._debug:
                log.debug("Setting Ambient Light integration time to {0}".format(itime))
            libmetawear.mbl_mw_als_ltr329_set_integration_time(self.board, itime)
        if measurement_rate is not None:
            mr = self._get_measurement_rate(measurement_rate)
            if self._debug:
                log.debug("Setting Ambient Light measurement rate to {0}".format(mr))
            libmetawear.mbl_mw_als_ltr329_set_measurement_rate(self.board, mr)

        if (gain is not None) or (integration_time is not None) or \
                (measurement_rate is not None):
            libmetawear.mbl_mw_als_ltr329_write_config(self.board)

    @require_ltr329
    def notifications(self, callback=None):
        """Subscribe or unsubscribe to notifications.

        Convenience method for handling ambient light sensor usage.

        Example:

        .. code-block:: python

            def al_callback(data):
                print(data)

            mwclient.ambient_light.notifications(al_callback)

        :param callable callback: Ambient Light notification callback function.
            If `None`, unsubscription to ambient light notifications
            is registered.

        """
        if callback is None:
            super(AmbientLightModule, self).notifications(None)
            self.stop()
        else:
            super(AmbientLightModule, self).notifications(
                data_handler(callback))
            self.start()

    @require_ltr329
    def start(self):
        """Starts luminance sampling"""
        libmetawear.mbl_mw_als_ltr329_start(self.board)

    @require_ltr329
    def stop(self):
        """Stops luminance sampling"""
        libmetawear.mbl_mw_als_ltr329_stop(self.board)
