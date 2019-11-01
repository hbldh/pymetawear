#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Main module for PyMetaWear

.. moduleauthor:: hbldh <henrik.blidh@nedomkull.com>

Created on 2016-03-30

"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import logging

from mbientlab.metawear import MetaWear, libmetawear

from pymetawear import add_stream_logger, modules


log = logging.getLogger(__name__)

_model_names = [
    "Unknown",
    "MetaWear R",
    "MetaWear RG",
    "MetaWear RPro",
    "MetaWear C",
    "MetaWear CPro",
    "MetaEnvironment",
    "MetaDetector",
    "MetaHealth",
    "MetaTracker",
    "MetaMotion R",
    "MetaMotion C"
]


class MetaWearClient(object):
    """A MetaWear communication client.

    This client bridges the gap between the
    `MetaWear C++ API <https://github.com/mbientlab/Metawear-CppAPI>`_
    and a GATT communication package in Python. It provides Pythonic
    interface to using the MetaWear boards, allowing for rapid
    development and testing.

    :param str address: A Bluetooth MAC address to a MetaWear board.
    :param str device: Specifying which Bluetooth device to use. Defaults
        to ``hci0`` on Linux. Not available on Windows.
    :param bool connect: If client should connect automatically, or wait for
        explicit :py:meth:`~MetaWearClient.connect` call. Default is ``True``.
    :param bool debug: If printout of all sent and received
        data should be done.

    """

    def __init__(self, address, device='hci0', connect=True, debug=False):
        """Constructor."""
        self._address = address
        self._debug = debug
        self._connect = connect

        if self._debug:
            add_stream_logger()
            log.info("Creating MetaWearClient for {0}...".format(address))

        self.mw = MetaWear(self._address, hci_mac=device)

        log.debug("Client started for BLE device {0}...".format(self._address))

        self.accelerometer = None
        #self.gpio = None
        self.gyroscope = None
        self.magnetometer = None
        self.barometer = None
        self.ambient_light = None
        self.switch = None
        self.settings = None
        self.temperature = None
        self.haptic = None
        self.led = None
        self.sensorfusion = None

        if connect:
            self.connect()

    def __enter__(self):
        if not self._connect:
            self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            self.disconnect()
        except Exception as e:
            print("Could not disconnect: {0}".format(e))

    @property
    def board(self):
        return self.mw.board

    @property
    def firmware_version(self):
        return self.mw.info['firmware']

    @property
    def hardware_version(self):
        return self.mw.info['hardware']

    @property
    def manufacturer(self):
        return self.mw.info['manufacturer']

    @property
    def serial(self):
        return self.mw.info['serial']

    @property
    def model(self):
        return self.mw.info['model']

    def __str__(self):
        return "MetaWearClient, {0}: {1}".format(
            self._address, self.mw.info)

    def __repr__(self):
        return "<MetaWearClient, {0}>".format(self._address)

    def connect(self):
        """Connect this client to the MetaWear device."""
        self.mw.connect()
        self._initialize_modules()

    def disconnect(self):
        """Disconnects this client from the MetaWear device."""
        self.mw.disconnect()

    def _initialize_modules(self):
        #self.gpio = modules.GpioModule(
        #    self.board,
        #    libmetawear.mbl_mw_metawearboard_lookup_module(
        #        self.board, modules.Modules.MBL_MW_MODULE_GPIO))
        self.accelerometer = modules.AccelerometerModule(
            self.board,
            libmetawear.mbl_mw_metawearboard_lookup_module(
                self.board, modules.Modules.MBL_MW_MODULE_ACCELEROMETER))
        self.gyroscope = modules.GyroscopeModule(
            self.board,
            libmetawear.mbl_mw_metawearboard_lookup_module(
                self.board, modules.Modules.MBL_MW_MODULE_GYRO))
        self.magnetometer = modules.MagnetometerModule(
            self.board,
            libmetawear.mbl_mw_metawearboard_lookup_module(
                self.board, modules.Modules.MBL_MW_MODULE_MAGNETOMETER))
        self.barometer = modules.BarometerModule(
            self.board,
            libmetawear.mbl_mw_metawearboard_lookup_module(
                self.board, modules.Modules.MBL_MW_MODULE_BAROMETER))
        self.ambient_light = modules.AmbientLightModule(
            self.board,
            libmetawear.mbl_mw_metawearboard_lookup_module(
                self.board, modules.Modules.MBL_MW_MODULE_AMBIENT_LIGHT))
        self.switch = modules.SwitchModule(self.board)
        self.settings = modules.SettingsModule(self.board)
        self.temperature = modules.TemperatureModule(self.board)
        self.haptic = modules.HapticModule(self.board)
        self.led = modules.LEDModule(self.board)
        self.sensorfusion = modules.SensorFusionModule(
            self.board,
            libmetawear.mbl_mw_metawearboard_lookup_module(
                self.board, modules.Modules.MBL_MW_MODULE_SENSOR_FUSION))
