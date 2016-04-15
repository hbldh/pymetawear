#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:mod:`haptic`
==================

Created by hbldh <henrik.blidh@nedomkull.com>
Created on 2016-04-14

"""

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import

from ctypes import c_float, c_uint16

from pymetawear import libmetawear
from pymetawear.modules.base import PyMetaWearModule


class HapticModule(PyMetaWearModule):
    def __init__(self, board, debug=False):
        super(HapticModule, self).__init__(board, debug)

    def __str__(self):
        return "{0}: {1}".format(self.module_name, self.sensor_name)

    def __repr__(self):
        return super(HapticModule, self).__repr__()

    @property
    def module_name(self):
        return 'Peripherals'

    @property
    def sensor_name(self):
        return 'Haptic'

    @property
    def data_signal(self):
        return self._data_signal_preprocess(
            libmetawear.mbl_mw_settings_get_battery_state_data_signal)

    def set_settings(self, **kwargs):
        """Set haptic settings.

        No settings to be set exists here.

        """
        pass

    def get_current_settings(self):
        return {}

    def get_possible_settings(self):
        return {}

    def notifications(self, callback=None):
        """Subscribe or unsubscribe to battery notifications.

        :param callable callback: Battery data notification callback
            function. If `None`, unsubscription to battery notifications
            is registered.

        """
        raise NotImplementedError("Haptic module has no notifications.")

    def start_motor(self, duty_cycle_per, pulse_width_ms):
        """Activate the haptic motor.

        :param float duty_cycle_per: Strength of the motor,
            between [0, 100] percent
        :param int pulse_width_ms: How long to run the motor, in milliseconds

        """
        libmetawear.mbl_mw_haptic_start_motor(
            c_float(float(duty_cycle_per)),
            c_uint16(int(pulse_width_ms)))

    def start_buzzer(self, pulse_width_ms):
        """Activate the haptic buzzer.

        :param int pulse_width_ms: How long to run the motor, in milliseconds

        """
        libmetawear.mbl_mw_haptic_start_buzzer(
            c_uint16(int(pulse_width_ms)))
