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
import os

from pymetawear import libmetawear, specs, add_stream_logger
from pymetawear import modules
from pymetawear.backends.pybluez import PyBluezBackend
from pymetawear.backends.pygatt import PyGattBackend
from pymetawear.exceptions import PyMetaWearException, PyMetaWearConnectionTimeout
from pymetawear.mbientlab.metawear.core import Status

log = logging.getLogger(__name__)


class MetaWearClient(object):
    """A MetaWear communication client.

    This client bridges the gap between the
    `MetaWear C++ API <https://github.com/mbientlab/Metawear-CppAPI>`_
    and a GATT communication package in Python. It provides Pythonic
    interface to using the MetaWear boards, allowing for rapid
    development and testing.

    :param str address: A Bluetooth MAC address to a MetaWear board.
    :param str backend: Either ``pygatt`` or ``pybluez``, designating which
        BLE communication backend that should be used.
    :param float timeout: Timeout for connecting to the MetaWear board. If
        ``None`` timeout defaults to the backend default.
    :param bool connect: If client should connect automatically, or wait for
        explicit :py:meth:`~MetaWearClient.connect` call. Default is ``True``.
    :param bool debug: If printout of all sent and received
        data should be done.

    """

    def __init__(self, address, backend='pygatt',
                 interface='hci0', timeout=None, connect=True, debug=False):
        """Constructor."""
        self._address = address
        self._debug = debug
        self._initialized = False

        if self._debug:
            add_stream_logger()
            log.info("Creating MetaWearClient for {0}...".format(address))

        # Handling of timeout.
        if timeout is None:
            timeout = os.environ.get('PYMETAWEAR_TIMEOUT', None)
            if timeout is not None:
                try:
                    timeout = float(timeout)
                except:
                    timeout = None

        if backend == 'pygatt':
            self._backend = PyGattBackend(
                self._address, interface=interface,
                timeout=timeout, debug=debug)
        elif backend == 'pybluez':
            self._backend = PyBluezBackend(
                self._address, interface=interface,
                timeout=timeout, debug=debug)
        else:
            raise PyMetaWearException("Unknown backend: {0}".format(backend))

        self.firmware_version = None
        self.model_version = None
        self.accelerometer = None
        self.gyroscope = None
        self.magnetometer = None
        self.barometer = None
        self.ambient_light = None
        self.switch = None
        self.battery = None
        self.temperature = None
        self.haptic = None
        self.led = None

        if connect:
            self.connect()

    def __str__(self):
        return "MetaWearClient, {0}, Model: {1}, Firmware: {2}".format(
            self.backend, self.model_version,
            ".".join([str(i) for i in self.firmware_version]) if self.firmware_version else None)

    def __repr__(self):
        return "<MetaWearClient, {0}>".format(self._address)

    @property
    def backend(self):
        """The backend object for this client.

        :return: The connected BLE backend.
        :rtype: :class:`pymetawear.backend.BLECommunicationBackend`

        """
        return self._backend

    @property
    def board(self):
        return self.backend.board

    def connect(self, clean_connect=False):
        """Connect this client to the MetaWear device.

        :param bool clean_connect: If old backend components should be replaced.
            Default is ``False``.

        """
        if self.backend.is_connected:
            return
        self.backend.connect(clean_connect=clean_connect)

        if self._debug:
            log.debug("Waiting for MetaWear board to be fully initialized...")

        while not self.backend.initialized:
            self.backend.sleep(0.1)

        # Check if initialization has been completed successfully.
        if self.backend.initialization_status != Status.OK:
            if self.backend.initialization_status == Status.ERROR_TIMEOUT:
                raise PyMetaWearConnectionTimeout("libmetawear initialization status 16: Timeout")
            else:
                raise PyMetaWearException("libmetawear initialization status {0}".format(
                    self.backend.initialization_status))

        # Read out firmware and model version.
        self.firmware_version = tuple(
            [int(x) for x in self.backend.read_gatt_char_by_uuid(
                specs.DEV_INFO_FIRMWARE_CHAR[1]).decode().split('.')])
        self.model_version = int(self.backend.read_gatt_char_by_uuid(
            specs.DEV_INFO_MODEL_CHAR[1]).decode())

        self._initialize_modules()

    def disconnect(self):
        """Disconnects this client from the MetaWear device."""
        libmetawear.mbl_mw_metawearboard_tear_down(self.board)
        libmetawear.mbl_mw_metawearboard_free(self.board)
        self.backend.disconnect()

    def get_handle(self, uuid, notify_handle=False):
        """Get handle for a characteristic UUID.

        :param uuid.UUID uuid: The UUID to get handle of.
        :param bool notify_handle:
        :return: Integer handle corresponding to the input characteristic UUID.
        :rtype: int

        """
        return self.backend.get_handle(uuid, notify_handle=notify_handle)

    def _set_logging_state(self, enabled=False):
        if enabled:
            libmetawear.mbl_mw_logging_start(self.board)
        else:
            libmetawear.mbl_mw_logging_stop(self.board)

    def _download_log(self, n_notifies):
        libmetawear.mbl_mw_logging_download(self.board, n_notifies)

    def soft_reset(self):
        """Issues a soft reset to the board."""
        libmetawear.mbl_mw_debug_reset(self.board)

    def _initialize_modules(self):
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
        self.battery = modules.BatteryModule(self.board, debug=self._debug)
        self.temperature = modules.TemperatureModule(
            self.board, debug=self._debug)
        self.haptic = modules.HapticModule(self.board, debug=self._debug)
        self.led = modules.LEDModule(self.board, debug=self._debug)
