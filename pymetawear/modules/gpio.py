#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
GPIO module
-----------

Created by hbldh <henrik.blidh@nedomkull.com> on 2016-04-14
Modified by lkasso <hello@mbientlab.com>

"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import re
import logging

from pymetawear import libmetawear

from mbientlab.metawear.cbindings import GpioPinChangeType, GpioPullMode, \
    GpioAnalogReadParameters, GpioAnalogReadMode
from pymetawear.modules.base import PyMetaWearModule, data_handler

log = logging.getLogger(__name__)


class GpioModule(PyMetaWearModule):
    """MetaWear gpio module implementation.

    :param ctypes.c_long board: The MetaWear board pointer value.
    :param int module_id: The module id of this accelerometer
        component, obtained from ``libmetawear``.
    :param bool debug: If ``True``, module prints out debug information.

    """

    def __init__(self, board, module_id, debug=False):
        super(GpioModule, self).__init__(board, debug)
        self.module_id = module_id
        
        self.current_pin = 0
        self.current_mode = 0
        self.current_read = 0

        self.pin = {}
        self.mode = {}
        self.read = {}
        
        gpio_pin_class = GpioPinChangeType
        gpio_mode_class = GpioPullMode
        gpio_read_class = GpioAnalogReadMode

        if gpio_pin_class is not None:
            # Parse possible pin outputs for GPIOs.
            for key, value in vars(gpio_pin_class).items():
                if re.search('^([A-Z]*)', key) and isinstance(value,int):
                    self.pin.update({key:value})
        
        if gpio_mode_class is not None:
            # Parse possible pull modes for GPIOs.
            for key, value in vars(gpio_mode_class).items():
                if re.search('^([A-Z]*)', key) and isinstance(value,int):
                    self.mode.update({key:value})
        
        if gpio_read_class is not None:
            # Parse possible analog read modes for GPIOs.
            for key, value in vars(gpio_read_class).items():
                if re.search('^([A-Z]*)', key) and isinstance(value,int):
                    self.read.update({key:value})
        
        if debug:
            log.setLevel(logging.DEBUG)

    def __str__(self):
        return "{0} {1}: Pin outputs: {2}, Pull modes: {3}, Read modes: {4}".format(
            self.module_name, self.sensor_name,
            [k for k in sorted(self.pin.keys())],
            [k for k in sorted(self.mode.keys())],
            [k for k in sorted(self.read.keys())])

    def __repr__(self):
        return str(self)

    @property
    def module_name(self):
        return "Gpio"

    @property
    def sensor_name(self):
        return self.module_name

    @property
    def data_signal(self):
        # TODO: Fix this pin issue!
        if self.analog:
            return libmetawear.mbl_mw_gpio_get_analog_input_data_signal(self.board, pin)
        elif self.digital:
            return libmetawear.mbl_mw_gpio_get_analog_input_data_signal(
                self.board, pin)
        else:
            return libmetawear.mbl_mw_gpio_get_pin_monitor_data_signal(
                self.board)

    def _get_pin(self, value):
        if value.lower() in self.pin:
            return self.pin.get(value.lower())
        else:
            raise ValueError(
                "Requested Pin Change Type ({0}) was not part of possible values: {1}".format(
                    value.lower(), self.pin.keys()))

    def _get_mode(self, value):
        if value.lower() in self.mode:
            return self.mode.get(value.lower())
        else:
            raise ValueError(
                "Requested Pull Mode ({0}) was not part of possible values: {1}".format(
                    value.lower(), self.mode.keys()))
    
    def _get_read(self, value):
        if value.lower() in self.read:
            return self.read.get(value.lower())
        else:
            raise ValueError(
                "Requested Analog Read Mode ({0}) was not part of possible values: {1}".format(
                    value.lower(), self.read.keys()))

    def get_current_settings(self):
        return "Pin change type: {} pull mode: {} analog read mode: {}".format(self.current_pin, self.current_mode, self.current_read)

    def get_possible_settings(self):
        return {
            'Pin change type': [x.lower() for x in sorted(
                self.pin.keys(), key=lambda x:(x.lower()))],
            'Pull mode': [x.lower() for x in sorted(
                self.mode.keys(), key=lambda x:(x.lower()))],
            'Analog read mode': [x.lower() for x in sorted(
                self.read.keys(), key=lambda x:(x.lower()))]
        }

    def set_settings(self, pin, rmode=None, pmode=None, ptype=None):
        if rmode is not None:
            rmode = self._get_read(rmode)
            if self._debug:
                log.debug("Setting the Analog Read Mode to {0}".format(rmode))
            self.current_mode = rmode

        if pmode is not None:
            self.current_ = pmode

        if ptype is not None:
            self.current_ = ptype

    def set_pull_mode(self, pin=None, pmode=None):
        libmetawear.mbl_mw_gpio_set_pull_mode(self.board, pin, pmode)
    
    def set_digital_out(self, pin=None):
        libmetawear.mbl_mw_gpio_set_digital_output(self.board, pin)

    def clear_digital_out(self, pin=None):
        libmetawear.mbl_mw_gpio_clear_digital_output(self.board, pin)
    
    def set_pin_change(self, pin=None, ptype=None):
        libmetawear.mbl_mw_gpio_set_pin_change_type(self.board, pin, ptype)

    def notifications(self, callback=None):
        """Subscribe or unsubscribe to accelerometer notifications.

        Convenience method for handling gpio usage.

        Example:

        .. code-block:: python

            def handle_gpio_notification(data)
                # Handle a (epoch_time, int value) type.
                epoch = data[0]
                value = data[1]
                print("[{0}] value: {1}".format(epoch, *value))

            mwclient.gpio.notifications(handle_gpio_notification)

        :param callable callback: Gpio notification callback function.
            If `None`, unsubscription to accelerometer notifications is registered.

        """

        if callback is None:
            self.stop()
            super(GpioModule, self).notifications(None)
        else:
            super(GpioModule, self).notifications(data_handler(callback))
            self.start()

    def start(self, pin=None):
        """Switches the gpio to active mode."""
        libmetawear.mbl_mw_gpio_start_pin_monitoring(self.board, pin)

    def stop(self, pin=None):
        """Switches the gpio to standby mode."""
        libmetawear.mbl_mw_gpio_stop_pin_monitoring(self.board, pin)
