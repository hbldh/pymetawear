#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""

.. moduleauthor:: hbldh <henrik.blidh@nedomkull.com>

Created on 2016-03-30

"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from ctypes import byref, cast, c_ubyte, c_uint, POINTER
import errno
import logging
import os

from pymetawear import libmetawear, specs, add_stream_logger
from pymetawear import modules
from pymetawear.backends.pybluez import PyBluezBackend
from pymetawear.backends.pygatt import PyGattBackend
from pymetawear.exceptions import PyMetaWearException, PyMetaWearConnectionTimeout
from pymetawear.mbientlab.metawear.cbindings import Const

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
    :param str backend: `pygatt`, designating which
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

        log.info("Backend starter with {0} for device address {1} with timeout {2}...".format(backend, address, timeout))
        self.firmware_version = None
        self.model_version = None
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

    @staticmethod
    def _lookup_path(path):
        return path if path is not None else ".metawear"

    @staticmethod
    def _lookup_name(name, address):
        return name if name is not None else address.replace(':','')

    def serialize(self, path=None, name=None):
        realpath = MetaWearClient._lookup_path(path)
        try:
            os.makedirs(realpath)
        except OSError as exception:
            if exception.errno != errno.EEXIST:
                raise
        finally:
            size = c_uint(0)
            state = cast(libmetawear.mbl_mw_metawearboard_serialize(self.board, byref(size)), POINTER(c_ubyte * size.value))
            python_array= []
            for i in range(0, size.value):
                python_array.append(state.contents[i])

            realfile = MetaWearClient._lookup_name(name, self._address)
            with open(os.path.join(os.getcwd(), realpath, realfile), "wb") as file:
                file.write(state.contents)
            libmetawear.mbl_mw_memory_free(state)

    def deserialize(self, path=None, name=None):
        state_path = os.path.join(os.getcwd(), MetaWearClient._lookup_path(path), MetaWearClient._lookup_name(name, self._address)) 
        if os.path.isfile(state_path):
            with(open(state_path, "rb")) as f:
                content = f.read()
                raw = (c_ubyte * len(content)).from_buffer_copy(content)
                libmetawear.mbl_mw_metawearboard_deserialize(self.board, raw, len(content))

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
        if self.backend.initialization_status != Const.STATUS_OK:
            if self.backend.initialization_status == Const.STATUS_ERROR_TIMEOUT:
                raise PyMetaWearConnectionTimeout("libmetawear initialization status 16: Timeout")
            else:
                raise PyMetaWearException("libmetawear initialization status {0}".format(
                    self.backend.initialization_status))

        # Read out firmware and model version.
        self.firmware_version_str = self.backend.read_gatt_char_by_uuid(specs.DEV_INFO_FIRMWARE_CHAR[1]).decode()
        self.firmware_version = tuple([int(x) for x in self.firmware_version_str.split('.')])
        self.model_version = int(self.backend.read_gatt_char_by_uuid(
            specs.DEV_INFO_MODEL_CHAR[1]).decode())
        self.model_name = _model_names[libmetawear.mbl_mw_metawearboard_get_model(self.board) + 1]

        self._initialize_modules()

    def free(self):
        """Frees unmanaged memory used by thie object"""
        libmetawear.mbl_mw_metawearboard_free(self.board)

    def disconnect(self, tear_down=True):
        """Disconnects this client from the MetaWear device."""
        if tear_down:
            libmetawear.mbl_mw_metawearboard_tear_down(self.board)
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
