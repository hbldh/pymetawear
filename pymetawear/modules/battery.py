#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:mod:`battery`
==================

Created by hbldh <henrik.blidh@nedomkull.com>
Created on 2016-04-14

"""

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import

import warnings

from pymetawear import libmetawear
from pymetawear.modules.base import PyMetaWearModule


class PyMetaWearBattery(PyMetaWearModule):
    def __init__(self, board, debug=False):
        super(PyMetaWearBattery, self).__init__(board, debug)

    def __str__(self):
        return "{0}: {1}".format(self.module_name, self.sensor_name)

    def __repr__(self):
        return super(PyMetaWearModule, self).__repr__()

    @property
    def module_name(self):
        return 'Settings'

    @property
    def sensor_name(self):
        return 'Battery'

    @property
    def data_signal(self):
        return self._data_signal_preprocess(
            libmetawear.mbl_mw_settings_get_battery_state_data_signal)

    def set_settings(self, **kwargs):
        """Set battery settings.

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
        super(PyMetaWearBattery, self).notifications(callback)

    def read_battery_state(self):
        """Triggers a battery state notification.

        N.B. that a :meth:`~notifications` call that registers a
        callback for battery state should have been done prior to calling
        this method.

        """
        if self.callback is None:
            warnings.warn("No battery callback is registered!", RuntimeWarning)
        libmetawear.mbl_mw_settings_read_battery_state(self.board)
