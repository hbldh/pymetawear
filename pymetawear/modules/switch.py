#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Switch module
-------------

Created by hbldh <henrik.blidh@nedomkull.com> on 2016-04-14

"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import logging

from pymetawear import libmetawear
from pymetawear.modules.base import PyMetaWearModule, data_handler

log = logging.getLogger(__name__)


class SwitchModule(PyMetaWearModule):
    """MetaWear Switch module implementation.

    :param ctypes.c_long board: The MetaWear board pointer value.
    :param bool debug: If ``True``, module prints out debug information.

    """

    def __init__(self, board, debug=False):
        super(SwitchModule, self).__init__(board, debug)

        if debug:
            log.setLevel(logging.DEBUG)

    def __str__(self):
        return "{0}".format(
            self.module_name)

    def __repr__(self):
        return str(self)

    @property
    def module_name(self):
        return "Switch"

    @property
    def data_signal(self):
        return libmetawear.mbl_mw_switch_get_state_data_signal(self.board)

    def notifications(self, callback=None):
        """Subscribe or unsubscribe to switch notifications.

        Convenience method for handling switch usage.

        Example:

        .. code-block:: python

            def switch_callback(data):
                # Handle dictionary with [epoch, value] keys.
                epoch = data["epoch"]
                value = data["value"]
                if value == 1:
                    print("[{0}] Switch pressed!".format(epoch))
                elif status == 0:
                    print("[{0}] Switch released!".format(epoch))

            mwclient.switch.notifications(switch_callback)

        :param callable callback: Switch notification callback function.
            If `None`, unsubscription to switch notifications is registered.

        """
        super(SwitchModule, self).notifications(
            data_handler(callback) if callback is not None else None)
