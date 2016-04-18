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

from ctypes import c_uint, cast, POINTER

from pymetawear import libmetawear
from pymetawear.exceptions import PyMetaWearException
from pymetawear.mbientlab.metawear.core import DataTypeId, BatteryState
from pymetawear.modules.base import PyMetaWearModule


class BatteryModule(PyMetaWearModule):
    """MetaWear Settings/Battery module implementation.

    :param ctypes.c_long board: The MetaWear board pointer value.
    :param bool debug: If ``True``, module prints out debug information.

    """

    def __init__(self, board, debug=False):
        super(BatteryModule, self).__init__(board, debug)
        self._internal_callback = None

    def __str__(self):
        return "{0}: {1}".format(self.module_name, self.sensor_name)

    def __repr__(self):
        return super(BatteryModule, self).__repr__()

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

    def notifications(self, callback=None):
        """Subscribe or unsubscribe to battery notifications.

        Convenience method for handling battery notifications.

        The data to the callback method comes as a tuple of two integer
        values, the first one representing the voltage and the second one
        is an integer in [0, 100] representing battery percentage.

        Example:

        .. code-block:: python

            def battery_callback(data):
                print("Voltage: {0}, Charge: {1}".format(
                    data[0], data[1]))

            mwclient.battery.notifications(battery_callback)
            mwclient.battery.read_battery_state()

        :param callable callback: Battery data notification callback
            function. If `None`, unsubscription to battery notifications
            is registered.

        """
        if callback is None:
            self._internal_callback = None
            super(BatteryModule, self).notifications(None)
        else:
            self._internal_callback = callback
            super(BatteryModule, self).notifications(
                self._callback_wrapper)

    def _callback_wrapper(self, data):
        if data.contents.type_id == DataTypeId.BATTERY_STATE:
            data_ptr = cast(data.contents.value, POINTER(BatteryState))
            self._internal_callback((int(data_ptr.contents.voltage),
                                    int(data_ptr.contents.charge)))
        else:
            raise PyMetaWearException(
                'Incorrect data type id: ' + str(data.contents.type_id))

    def read_battery_state(self):
        """Triggers a battery state notification.

        N.B. that a :meth:`~notifications` call that registers a
        callback for battery state should have been done prior to calling
        this method.

        """
        if self.callback is None:
            warnings.warn("No battery callback is registered!", RuntimeWarning)
        libmetawear.mbl_mw_settings_read_battery_state(self.board)
