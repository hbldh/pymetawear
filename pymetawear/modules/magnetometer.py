#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Magnetometer module
-------------------

Created by jboeer <jonas.boeer@kinemic.de> on 2016-09-07

"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import re
import logging

from pymetawear import libmetawear
from pymetawear.exceptions import PyMetaWearException
from mbientlab.metawear.cbindings import MagBmm150Odr, MagBmm150Preset
from pymetawear.modules.base import PyMetaWearLoggingModule, Modules, data_handler

log = logging.getLogger(__name__)


def require_bmm150(f):
    def wrapper(*args, **kwargs):
        if getattr(args[0], 'mag_p_class', None) is None:
            raise PyMetaWearException("There is not Magnetometer "
                                      "module on your MetaWear board!")
        return f(*args, **kwargs)

    return wrapper


class MagnetometerModule(PyMetaWearLoggingModule):
    """MetaWear accelerometer module implementation.

    :param ctypes.c_long board: The MetaWear board pointer value.
    :param int module_id: The module id of this accelerometer
        component, obtained from ``libmetawear``.
    :param bool debug: If ``True``, module prints out debug information.

    """

    def __init__(self, board, module_id):
        super(MagnetometerModule, self).__init__(board)
        self.current_power_preset = None

        self.module_id = module_id
        
        self.power_presets = {}
        self.odr = {}

        if self.module_id == Modules.MBL_MW_MODULE_NA:
            # No magnetometer present!
            self.mag_o_class = None
            self.mag_p_class = None
        else:
            self.mag_o_class = MagBmm150Odr
            self.mag_p_class = MagBmm150Preset

        if self.mag_p_class is not None:
            # Parse possible presets for this magnetometer.
            for key, value in vars(self.mag_p_class).items():
                if re.search('^([A-Z\_]*)', key) and isinstance(value,int):
                    self.power_presets.update({key.lower(): value})

        if self.mag_o_class is not None:
            # Parse possible data rates for this magnetometer.
            for key, value in vars(self.mag_o_class).items():
                if re.search('^_([0-9\_]*Hz)', key) and isinstance(value,int):
                    self.odr.update({key[1:-2]: value})

    def __str__(self):
        return "{0} {1}: Power presets: {2}".format(
            self.module_name, self.sensor_name,
            [float(k) for k in sorted(self.power_presets.keys())])

    def __repr__(self):
        return str(self)

    @property
    def module_name(self):
        return "Magnetometer"

    @property
    def sensor_name(self):
        if self.mag_p_class is not None:
            return self.mag_p_class.__name__.replace(
                'Mag', '').replace('Preset', '')
        else:
            return ''

    @property
    @require_bmm150
    def data_signal(self):
        return libmetawear.mbl_mw_mag_bmm150_get_b_field_data_signal(self.board)

    def _get_power_preset(self, value):
        if value.lower() in self.power_presets:
            return self.power_presets.get(value.lower())
        else:
            raise ValueError("Requested power preset ({0}) was not part of "
                             "possible values: {1}".format(value.lower(), [self.power_presets.keys()]))

    @require_bmm150
    def get_current_settings(self):
        return {
            'power_preset': self.current_power_preset
        }

    @require_bmm150
    def get_possible_settings(self):
        return {
            'power_preset': [sorted(self.power_presets.keys(), key=lambda x:(x.lower()))],
        }

    @require_bmm150
    def set_settings(self, power_preset=None):
        """Set magnetometer settings.

         .code-block:: python

            mwclient.magnetometer.set_settings(power_preset="LOW_POWER")

        Call :meth:`~get_possible_settings` to see which values
        that can be set for this sensor.

        :param str power_preset: The power preset, influencing the data rate,
            accuracy and power consumption

        """
        if power_preset is not None:
            pp = self._get_power_preset(power_preset)
            log.debug("Setting Magnetometer power preset to {0}".format(pp))
            libmetawear.mbl_mw_mag_bmm150_set_preset(self.board, pp)
            self.current_power_preset = pp

    @require_bmm150
    def notifications(self, callback=None):
        """Subscribe or unsubscribe to magnetometer notifications.

        Convenience method for handling magnetometer usage.

        Example:

        .. code-block:: python

            def handle_notification(data):
                # Handle dictionary with [epoch, value] keys.
                epoch = data["epoch"]
                xyz = data["value"]
                print(str(data))

            mwclient.magnetometer.notifications(handle_notification)

        :param callable callback: Magnetometer notification callback function.
            If `None`, unsubscription to magnetometer notifications is registered.

        """
        if callback is None:
            self.stop()
            self.toggle_sampling(False)
            super(MagnetometerModule, self).notifications(None)
        else:
            super(MagnetometerModule, self).notifications(data_handler(callback))
            self.toggle_sampling(True)
            self.start()

    @require_bmm150
    def start(self):
        """Switches the magnetometer to active mode."""
        libmetawear.mbl_mw_mag_bmm150_start(self.board)

    @require_bmm150
    def stop(self):
        """Switches the magnetometer to standby mode."""
        libmetawear.mbl_mw_mag_bmm150_stop(self.board)

    @require_bmm150
    def toggle_sampling(self, enabled=True):
        """Enables or disables magnetometer sampling.

        :param bool enabled: Desired state of the magnetometer.

        """
        if enabled:
            libmetawear.mbl_mw_mag_bmm150_enable_b_field_sampling(self.board)
        else:
            libmetawear.mbl_mw_mag_bmm150_disable_b_field_sampling(self.board)
