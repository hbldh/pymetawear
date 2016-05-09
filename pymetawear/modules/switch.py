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

from functools import wraps
from ctypes import c_uint, cast, POINTER

from pymetawear import libmetawear
from pymetawear.exceptions import PyMetaWearException
from pymetawear.mbientlab.metawear.core import DataTypeId, CartesianFloat
from pymetawear.modules.base import PyMetaWearModule


class SwitchModule(PyMetaWearModule):
    """MetaWear Switch module implementation.

    :param ctypes.c_long board: The MetaWear board pointer value.
    :param bool debug: If ``True``, module prints out debug information.

    """

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
    def data_signal(self):
        return self._data_signal_preprocess(
            libmetawear.mbl_mw_switch_get_state_data_signal)

    def notifications(self, callback=None):
        """Subscribe or unsubscribe to switch notifications.

        Convenience method for handling switch usage.

        Example:

        .. code-block:: python

            def switch_callback(data):
                epoch = data[0]
                status = data[1]
                if status == 1:
                    print("[{0}] Switch pressed!".format(epoch))
                elif status == 0:
                    print("[{0}] Switch released!".format(epoch))

            mwclient.switch.notifications(switch_callback)

        :param callable callback: Switch notification callback function.
            If `None`, unsubscription to switch notifications is registered.

        """
        super(SwitchModule, self).notifications(
            switch_data(callback) if callback is not None else None)


def switch_data(func):
    @wraps(func)
    def wrapper(data):
        if data.contents.type_id == DataTypeId.UINT32:
            epoch = int(data.contents.epoch)
            data_ptr = cast(data.contents.value, POINTER(c_uint))
            func((epoch, data_ptr.contents.value))
        else:
            raise PyMetaWearException('Incorrect data type id: {0}'.format(
                data.contents.type_id))
    return wrapper
