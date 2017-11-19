#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Settings module
---------------

Created by hbldh <henrik.blidh@nedomkull.com> on 2016-04-14

"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import logging
import warnings
from ctypes import c_ubyte, create_string_buffer, cast, POINTER

from pymetawear import libmetawear
from pymetawear.modules.base import PyMetaWearModule, data_handler

log = logging.getLogger(__name__)


class SettingsModule(PyMetaWearModule):
    """MetaWear Settings module implementation.

    :param ctypes.c_long board: The MetaWear board pointer value.
    :param bool debug: If ``True``, module prints out debug information.

    """

    def __init__(self, board, debug=False):
        super(SettingsModule, self).__init__(board, debug)

        self.current_name = None
        self.current_tx_power = None
        self.current_ad_interval = None
        self.current_ad_timeout = None
        self.current_min_conn_interval = None
        self.current_max_conn_interval = None
        self.current_latency = None
        self.current_timeout = None

        self.possible_tx_power = [4, 0, -4, -8, -12, -16, -20, -30]

        if debug:
            log.setLevel(logging.DEBUG)

    def __str__(self):
        return "{0}: {1}".format(self.module_name, self.sensor_name)

    def __repr__(self):
        return super(SettingsModule, self).__repr__()

    @property
    def module_name(self):
        return 'Settings'

    @property
    def sensor_name(self):
        return self.module_name

    @property
    def data_signal(self):
        return libmetawear.mbl_mw_settings_get_battery_state_data_signal(self.board)

    def set_device_name(self, name=None):
        if name is not None and len(name) <= 8:
            self.current_name = name
            if self._debug:
                log.debug("Setting device name to {0}".format(name))
            fname = create_string_buffer(name, 8)
            bname = cast(fname, POINTER(c_ubyte))
            libmetawear.mbl_mw_settings_set_device_name(self.board, bname, len(fname.raw))  
        elif self._debug:
            log.debug("{0} is not a valid name".format(name))
    
    def set_tx_power(self, power=None):
        if power is not None:
            if power in self.possible_tx_power:
                self.current_tx_power = power 
                if self._debug:
                    log.debug("Setting device TX power to {0}".format(power))
                libmetawear.mbl_mw_settings_set_tx_power(self.board, power) 
            elif self._debug:
                log.debug("{0} is not a valid value for TX power. Valid values are {1}".format(power, self.possible_tx_power))

    def set_ad_interval(self, interval=None, timeout=None):
        if interval is not None and timeout is not None:
            if (interval >= 0 and interval <= 65535) and (timeout >= 0 and timeout <= 180):
                self.current_ad_interval = interval
                self.current_ad_timeout = timeout
                if self._debug:
                    log.debug("Setting device interval to {0} and timeout to {1}".format(interval, timeout))
                libmetawear.mbl_mw_settings_set_ad_interval(self.board, interval, timeout) 
            elif self._debug:
                log.debug("Invalid values for timeout and interval")
   
    def start_advertising(self):
        if self._debug:
            log.debug("Setting device to start advertising")
        libmetawear.mbl_mw_settings_start_advertising(self.board) 

    def set_connection_parameters(self, min_conn_interval=None, max_conn_interval=None, latency=None, timeout=None):
        if min_conn_interval is not None and max_conn_interval is not None and latency is not None and timeout is not None:
            if ((min_conn_interval >= 7.5) and (max_conn_interval <= 4000) and (latency >= 0 and latency <= 1000) and (timeout >= 10 and timeout <= 32000)):
                self.current_max_conn_interval = max_conn_interval
                self.current_max_conn_interval = max_conn_interval
                self.current_latency = latency 
                self.current_timeout = timeout
                if self._debug:
                    log.debug("Setting device min connection interval to {0}, max connection interval to {1}, latency to {2}, and timeout to {3}".format(min_conn_interval, max_conn_interval, latency, timeout))
                libmetawear.mbl_mw_settings_set_connection_parameters(self.board, min_conn_interval, max_conn_interval, latency, timeout) 
            elif self._debug:
                log.debug("Invalid values for min connection interval, max connection interval, timeout and latency")
    
    def set_scan_response(self, response=None):
        if response is not None:
            self.current_scan_response = response
            if self._debug:
                log.debug("Setting scan response to {0}".format(response))
            fresponse = create_string_buffer(response)
            bresponse = cast(fresponse, POINTER(c_ubyte))
            libmetawear.mbl_mw_settings_set_device_name(self.board, bresponse, len(fresponse))  
    
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

            mwclient.settings.notifications(battery_callback)
            mwclient.settings.read_battery_state()

        :param callable callback: Battery data notification callback
            function. If `None`, unsubscription to battery notifications
            is registered.

        """
        super(SettingsModule, self).notifications(
            data_handler(callback) if callback is not None else None)

    def read_battery_state(self):
        """Triggers a battery state notification.

        N.B. that a :meth:`~notifications` call that registers a
        callback for battery state should have been done prior to calling
        this method.

        """
        if self.callback is None:
            warnings.warn("No battery callback is registered!", RuntimeWarning)
        libmetawear.mbl_mw_datasignal_read(self.data_signal)
    
    def disconnected_event(self):
        """Create a disconnect event.

        Convenience method for sending commands during a disconnect event.

        """
        event = libmetawear.mbl_mw_settings_get_disconnect_event(self.board)
        return event
