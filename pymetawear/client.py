#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""

.. moduleauthor:: hbldh <henrik.blidh@nedomkull.com>

Created on 2016-03-30

"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import logging

from mbientlab.metawear import MetaWear, libmetawear
# Temporary for money patch
from mbientlab.metawear.cbindings import FnVoid_VoidP_Int, Const
from mbientlab.metawear import Event

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


def _connect(self, **kwargs):
    """Monkey patch for connecting.

    Will be removed after PR fixing issue is accepted.
    """
    try:
        self.gatt.connect(True, channel_type='random')
    except RuntimeError as e:
        # gattlib.connect's `wait=True` requires elevated permission
        # or modified capabilities.
        # It still connects, but a RuntimeError is raised. Check if
        # `self.gatt` is connected, and rethrow exception otherwise.
        if not self.gatt.is_connected():
            raise e

    self.services = set()
    for s in self.gatt.discover_primary():
        self.services.add(s['uuid'])

    self.characteristics = {}
    for c in self.gatt.discover_characteristics():
        self.characteristics[c['uuid']] = c['value_handle']

    if 'hardware' not in self.info:
        self.info['hardware'] = self.gatt.read_by_uuid(
            "00002a27-0000-1000-8000-00805f9b34fb")[0]

    if 'manufacturer' not in self.info:
        self.info['manufacturer'] = self.gatt.read_by_uuid(
            "00002a29-0000-1000-8000-00805f9b34fb")[0]

    if 'serial' not in self.info:
        self.info['serial'] = self.gatt.read_by_uuid(
            "00002a25-0000-1000-8000-00805f9b34fb")[0]

    if 'model' not in self.info:
        self.info['model'] = self.gatt.read_by_uuid(
            "00002a24-0000-1000-8000-00805f9b34fb")[0]

    if not self.in_metaboot_mode:
        init_event = Event()

        def init_handler(device, status):
            self.init_status = status
            init_event.set()

        init_handler_fn = FnVoid_VoidP_Int(init_handler)
        libmetawear.mbl_mw_metawearboard_initialize(self.board, init_handler_fn)
        init_event.wait()

        if self.init_status != Const.STATUS_OK:
            self.disconnect()
            raise RuntimeError(
                "Error initializing the API (%d)" % self.init_status)

        if 'serialize' not in kwargs or kwargs['serialize']:
            self.serialize()
    else:
        self.info['firmware'] = self.gatt.read_by_uuid(
            "00002a26-0000-1000-8000-00805f9b34fb")[0]


MetaWear.connect = _connect


class MetaWearClient(object):
    """A MetaWear communication client.

    This client bridges the gap between the
    `MetaWear C++ API <https://github.com/mbientlab/Metawear-CppAPI>`_
    and a GATT communication package in Python. It provides Pythonic
    interface to using the MetaWear boards, allowing for rapid
    development and testing.

    :param str address: A Bluetooth MAC address to a MetaWear board.
    :param str device: Specifying which Bluetooth device to use. Defaults
        to ``hci0``.
    :param float timeout: Timeout for connecting to the MetaWear board. If
        ``None`` timeout defaults to the backend default.
    :param bool connect: If client should connect automatically, or wait for
        explicit :py:meth:`~MetaWearClient.connect` call. Default is ``True``.
    :param bool debug: If printout of all sent and received
        data should be done.

    """

    def __init__(self, address, device='hci0', connect=True, debug=False):
        """Constructor."""
        self._address = address
        self._debug = debug

        if self._debug:
            add_stream_logger()
            log.info("Creating MetaWearClient for {0}...".format(address))

        self.mw = MetaWear(self._address, device=device)

        log.info("Client started for BLE device {0} on {1}...".format(
            self._address, device))

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
        #        self.board, modules.Modules.MBL_MW_MODULE_GPIO),
        #    debug=self._debug)
        self.accelerometer = modules.AccelerometerModule(
            self.board,
            libmetawear.mbl_mw_metawearboard_lookup_module(
                self.board, modules.Modules.MBL_MW_MODULE_ACCELEROMETER),
            debug=self._debug)
        self.gyroscope = modules.GyroscopeModule(
            self.board,
            libmetawear.mbl_mw_metawearboard_lookup_module(
                self.board, modules.Modules.MBL_MW_MODULE_GYRO),
            debug=self._debug)
        self.magnetometer = modules.MagnetometerModule(
            self.board,
            libmetawear.mbl_mw_metawearboard_lookup_module(
                self.board, modules.Modules.MBL_MW_MODULE_MAGNETOMETER),
            debug=self._debug)
        self.barometer = modules.BarometerModule(
            self.board,
            libmetawear.mbl_mw_metawearboard_lookup_module(
                self.board, modules.Modules.MBL_MW_MODULE_BAROMETER),
            debug=self._debug)
        self.ambient_light = modules.AmbientLightModule(
            self.board,
            libmetawear.mbl_mw_metawearboard_lookup_module(
                self.board, modules.Modules.MBL_MW_MODULE_AMBIENT_LIGHT),
            debug=self._debug)
        self.switch = modules.SwitchModule(self.board, debug=self._debug)
        self.settings = modules.SettingsModule(self.board, debug=self._debug)
        self.temperature = modules.TemperatureModule(
            self.board, debug=self._debug)
        self.haptic = modules.HapticModule(self.board, debug=self._debug)
        self.led = modules.LEDModule(self.board, debug=self._debug)
        self.sensorfusion = modules.SensorFusionModule(
            self.board,
            libmetawear.mbl_mw_metawearboard_lookup_module(
                self.board, modules.Modules.MBL_MW_MODULE_SENSOR_FUSION),
            debug=self._debug)
