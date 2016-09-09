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
from ctypes import cast, POINTER

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
                epoch = data[0]
                battery = data[1]
                print("[{0}] Voltage: {1}, Charge: {2}".format(
                    epoch, battery[0], battery[1]))

            mwclient.battery.notifications(battery_callback)
            mwclient.battery.read_battery_state()

        :param callable callback: Battery data notification callback
            function. If `None`, unsubscription to battery notifications
            is registered.

        """
        super(BatteryModule, self).notifications(
            battery_data(callback) if callback is not None else None)

    def read_battery_state(self):
        """Triggers a battery state notification.

        N.B. that a :meth:`~notifications` call that registers a
        callback for battery state should have been done prior to calling
        this method.

        """
        if self.callback is None:
            warnings.warn("No battery callback is registered!", RuntimeWarning)
        libmetawear.mbl_mw_datasignal_read(self.data_signal)


def battery_data(func):
    @wraps(func)
    def wrapper(data):
        if data.contents.type_id == DataTypeId.BATTERY_STATE:
            epoch = int(data.contents.epoch)
            data_ptr = cast(data.contents.value, POINTER(BatteryState))
            func((epoch, (int(data_ptr.contents.voltage),
                          int(data_ptr.contents.charge))))
        else:
            raise PyMetaWearException('Incorrect data type id: {0}'.format(
                data.contents.type_id))
    return wrapper
