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

import warnings
from functools import wraps
from ctypes import c_uint, cast, POINTER, c_long, c_float

from pymetawear import libmetawear, IS_64_BIT
from pymetawear.exceptions import PyMetaWearException
from pymetawear.mbientlab.metawear.core import DataTypeId
from pymetawear.mbientlab.metawear.sensor import MultiChannelTemperature
from pymetawear.modules.base import PyMetaWearModule

_CHANNEL_ID_TO_SOURCE_NAME = {
    -1: 'Invalid',
    0: 'On-Die',
    1: 'External',
    2: 'BMP280',
    3: 'On-Board'
}
_CHANNEL_ID_TO_SOURCE_NAME_4 = {
    0: 'On-Die',
    1: 'On-Board',
    2: 'External',
    3: 'BMP280'
}
_CHANNEL_ID_TO_SOURCE_NAME_2 = {
    0: 'On-Die',
    1: 'External',
}

class TemperatureModule(PyMetaWearModule):
    """MetaWear Temperature module implementation.

    :param ctypes.c_long board: The MetaWear board pointer value.
    :param bool debug: If ``True``, module prints out debug information.

    """

    def __init__(self, board, debug=False):
        super(TemperatureModule, self).__init__(board, debug)
        self._active_channel = 0

        self.n_channels = int(
            libmetawear.mbl_mw_multi_chnl_temp_get_num_channels(self.board))
        self.channels = {}
        if self.n_channels == 4:
            self._channel_source_mapping = _CHANNEL_ID_TO_SOURCE_NAME_4
        elif self.n_channels == 2:
            self._channel_source_mapping = _CHANNEL_ID_TO_SOURCE_NAME_2
        else:
            self._channel_source_mapping = _CHANNEL_ID_TO_SOURCE_NAME

        self._reverse_channel_source_mapping = {
            v: k for k,v in self._channel_source_mapping.items()}

        for i in range(self.n_channels):
            source_enum = libmetawear.mbl_mw_multi_chnl_temp_get_source(
                self.board, i)
            self.channels[self._channel_source_mapping.get(source_enum)] = source_enum

    def __str__(self):
        return "{0}".format(self.module_name)

    def __repr__(self):
        return str(self)

    @property
    def module_name(self):
        return "Temperature"

    @property
    def data_signal(self):
        data_signal_func = \
            libmetawear.mbl_mw_multi_chnl_temp_get_temperature_data_signal
        if IS_64_BIT:
            data_signal_func.restype = c_long
            data_signal = c_long(data_signal_func(
                self.board, self._active_channel))
        else:
            data_signal = data_signal_func(self.board, self._active_channel)
        return data_signal

    def configure_external_thermistor(self, channel_id, data_pin,
                                      pulldown_pin, active_high):
        """Configure the external thermistor.

        :param channel_id: Channel ID of the external thermistor
        :param int data_pin: GPIO pin reading the data
        :param int pulldown_pin: GPIO pin the pulldown resistor is connected to
        :param int active_high: Zero if the pulldown pin is not active high,
            non-zero if active high

        """
        libmetawear.mbl_mw_multi_chnl_temp_configure_ext_thermistor(
            self.board, channel_id, data_pin, pulldown_pin, active_high)

    def get_possible_settings(self):
        """Get the possible settings for this module.

        :return: Dict with the names of the possible channel choices.

        """
        return {
            'channel': [c for c in sorted(
                self.channels.keys(), key=lambda x: self.channels[x])],
        }

    def get_current_settings(self):
        """Get the current settings for this module.

        :return: Dict with the name of the currently active channel.

        """
        return {
            'channel': _CHANNEL_ID_TO_SOURCE_NAME.get(self._active_channel)
        }

    def set_settings(self, channel=None):
        """Set temperature channel settings.

         .. code-block:: python

            mwclient.temperature.set_settings(channel='On-Die')

        Call :meth:`~get_possible_settings` to see which values
        that can be set for this sensor.

        :param str channel: The name of the temperature channel to make active.

        """
        if channel is not None:
            if channel in self.channels:
                self._active_channel = self._reverse_channel_source_mapping.get(channel)
            else:
                warnings.warn("Desired channel {0} was not one of the possible ones: {1}.".format(
                    channel, self.get_possible_settings().get('channel')))

    def read_temperature(self):
        """Triggers a temperature notification.

        N.B. that a :meth:`~notifications` call that registers a
        callback for temperature should have been done prior to calling
        this method.

        """
        if self.callback is None:
            warnings.warn("No temperature callback is registered!", RuntimeWarning)
        libmetawear.mbl_mw_datasignal_read(self.data_signal)

    def notifications(self, callback=None):
        """Subscribe or unsubscribe to temperature notifications.

        Convenience method for handling temperature usage.

        Example:

        .. code-block:: python

            def temperature_callback(data):
                epoch = data[0]
                temp = data[1]
                print("[{0}] Temperature {1}".format(epoch, temp))

            mwclient.temperature_func.notifications(temperature_callback)

        :param callable callback: Temperature notification callback function.
            If `None`, unsubscription to temperature_func notifications is registered.

        """
        super(TemperatureModule, self).notifications(
            temperature_func(callback) if callback is not None else None)


def temperature_func(func):
    @wraps(func)
    def wrapper(data):
        if data.contents.type_id == DataTypeId.FLOAT:
            epoch = int(data.contents.epoch)
            data_ptr = cast(data.contents.value, POINTER(c_float))
            func((epoch, data_ptr.contents.value))
        else:
            raise PyMetaWearException('Incorrect data type id: {0}'.format(
                data.contents.type_id))
    return wrapper
