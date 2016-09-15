#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""

.. moduleauthor:: jboeer <jonas.boeer@kinemic.de>

Created: 2016-04-14

"""

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import

import re
from functools import wraps
from ctypes import cast, POINTER

from pymetawear import libmetawear
from pymetawear.exceptions import PyMetaWearException
from pymetawear.mbientlab.metawear import sensor
from pymetawear.mbientlab.metawear.core import DataTypeId, CartesianFloat
from pymetawear.modules.base import PyMetaWearModule, Modules


def require_bmm150(f):
    def wrapper(*args, **kwargs):
        if getattr(args[0], 'mag_class', None) is None:
            raise PyMetaWearException("There is not Magnetometer "
                                      "module on your MetaWear board!")
        return f(*args, **kwargs)

    return wrapper


class MagnetometerModule(PyMetaWearModule):
    """MetaWear accelerometer module implementation.

    :param ctypes.c_long board: The MetaWear board pointer value.
    :param int module_id: The module id of this accelerometer
        component, obtained from ``libmetawear``.
    :param bool debug: If ``True``, module prints out debug information.

    """

    def __init__(self, board, module_id, debug=False):
        super(MagnetometerModule, self).__init__(board, debug)
        self.module_id = module_id

        if self.module_id == Modules.MBL_MW_MODULE_NA:
            # No magnetometer present!
            self.mag_class = None
        else:
            self.mag_class = sensor.MagnetometerBmm150

        if self.mag_class is not None:
            self.power_presets = {re.search('^POWER_PRESET_([A-Z\_]*)', k).groups()[0].lower():
                                  getattr(self.mag_class, k, None) for k in filter(
                lambda x: x.startswith('POWER_PRESET_'), vars(self.mag_class))}

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
        if self.mag_class is not None:
            return self.mag_class.__name__.replace('Magnetometer', '')
        else:
            return ''

    @property
    @require_bmm150
    def data_signal(self):
        return self._data_signal_preprocess(
            libmetawear.mbl_mw_mag_bmm150_get_b_field_data_signal)

    def _get_power_preset(self, value):
        if value.lower() in self.power_presets:
            return self.power_presets.get(value.lower())
        else:
            raise ValueError("Requested power preset ({0}) was not part of "
                             "possible values: {1}".format(value.lower(), [self.power_presets.keys()]))

    @require_bmm150
    def get_current_settings(self):
        raise NotImplementedError()

    @require_bmm150
    def get_possible_settings(self):
        return {
            'power_preset': [sorted(self.power_presets.keys(), key=lambda x:(x.lower()))]
        }

    @require_bmm150
    def set_settings(self, power_preset):
        """Set magnetometer settings.

         .code-block:: python

            mwclient.magnetometer.set_settings(power_preset="LOW_POWER")

        Call :meth:`~get_possible_settings` to see which values
        that can be set for this sensor.

        :param str power_preset: The power preset, influencing the data rate,
            accuracy and power consumption

        """
        pp = self._get_power_preset(power_preset)
        if self._debug:
            print("Setting Magnetometer power preset to {0}".format(pp))
        libmetawear.mbl_mw_mag_bmm150_set_power_preset(self.board, pp)

    @require_bmm150
    def notifications(self, callback=None):
        """Subscribe or unsubscribe to magnetometer notifications.

        Convenience method for handling magnetometer usage.

        Example:

        .. code-block:: python

            def handle_notification(data):
                # Handle a (epoch_time, (x,y,z)) magnetometer tuple.
                epoch = data[0]
                xyz = data[1]
                print("[{0}] X: {1}, Y: {2}, Z: {3}".format(epoch, *xyz))

            mwclient.magnetometer.notifications(handle_notification)

        :param callable callback: Magnetometer notification callback function.
            If `None`, unsubscription to magnetometer notifications is registered.

        """
        if callback is None:
            self.stop()
            self.toggle_sampling(False)
            super(MagnetometerModule, self).notifications(None)
        else:
            super(MagnetometerModule, self).notifications(
                sensor_data(callback))
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
