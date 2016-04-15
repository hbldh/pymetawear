#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:mod:`switch`
==================

Created by hbldh <henrik.blidh@nedomkull.com>
Created on 2016-04-14

"""

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import

from pymetawear import libmetawear
from pymetawear.modules.base import PyMetaWearModule


class SwitchModule(PyMetaWearModule):

    def __init__(self, board, debug=False):
        super(SwitchModule, self).__init__(board, debug)

    def __str__(self):
        return "{0}".format(
            self.module_name)

    def __repr__(self):
        return str(self)

    @property
    def module_name(self):
        return "Switch"

    @property
    def sensor_name(self):
        return 'Switch'

    @property
    def data_signal(self):
        return self._data_signal_preprocess(
            libmetawear.mbl_mw_switch_get_state_data_signal)

    def get_settings(self):
        return {}

    def get_current_settings(self):
        return {}

    def get_possible_settings(self):
        return {}

    def set_settings(self, **kwargs):
        """Set switch settings.

         No settings to be set exists here.

        """
        pass

    def notifications(self, callback=None):
        """Subscribe or unsubscribe to switch notifications.

        Convenience method for handling switch usage.

        Example:

        .. code-block:: python

            from ctypes import POINTER, c_uint, cast

            def switch_callback(data):
                data_ptr = cast(data.contents.value, POINTER(c_uint))
                if data_ptr.contents.value == 1:
                    print("Switch pressed!")
                elif data_ptr.contents.value == 0:
                    print("Switch released!")

            mwclient.switch.notifications(switch_callback)

        :param callable callback: Switch notification callback function.
            If `None`, unsubscription to switch notifications is registered.

        """
        super(SwitchModule, self).notifications(callback)
