#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""

.. moduleauthor:: hbldh <henrik.blidh@nedomkull.com>

Created on 2016-03-30

"""

from __future__ import division
from __future__ import print_function
# from __future__ import unicode_literals
from __future__ import absolute_import

import os
import time
import subprocess
import signal

from pymetawear import libmetawear, specs
from pymetawear.exceptions import *
from pymetawear import modules
try:
    from pymetawear.backends.pygatt import PyGattBackend
except ImportError:
    PyGattBackend = None
try:
    from pymetawear.backends.pybluez import PyBluezBackend
except ImportError:
    PyBluezBackend = None
try:
    from pymetawear.backends.bluepy import BluepyBackend
except ImportError:
    BluepyBackend = None


def discover_devices(timeout=5):
    """Discover Bluetooth Low Energy Devices nearby.

    Using hcitool in subprocess, since DiscoveryService in pybluez/gattlib
    requires sudo, and hcitool can be allowed to do scan without elevated
    permission.

    .. code-block:: bash

        $ sudo apt-get install libcap2-bin

    installs linux capabilities manipulation tools.

    .. code-block:: bash

        $ sudo setcap 'cap_net_raw,cap_net_admin+eip' `which hcitool`

    sets the missing capabilities on the executable quite like the setuid bit.

    **References:**

    * `StackExchange, hcitool without sudo <https://unix.stackexchange.com/questions/96106/bluetooth-le-scan-as-non-root>`_
    * `StackOverflow, hcitool lescan with timeout <https://stackoverflow.com/questions/26874829/hcitool-lescan-will-not-print-in-real-time-to-a-file>`_

    :param int timeout: Duration of scanning.
    :return: List of tuples with `(address, name)`.
    :rtype: list

    """
    p = subprocess.Popen(["hcitool", "lescan"], stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    time.sleep(timeout)
    os.kill(p.pid, signal.SIGINT)
    out, err = p.communicate()
    if len(out) == 0 and len(err) > 0:
        if err == b'Set scan parameters failed: Operation not permitted\n':
            raise PyMetaWearException("Missing capabilites for hcitool!")
        if err == b'Set scan parameters failed: Input/output error\n':
            raise PyMetaWearException("Could not perform scan.")
    ble_devices = list(set([tuple(x.split(' ')) for x in
                            filter(None, out.decode('utf8').split('\n')[1:])]))
    return ble_devices


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
    :param bool debug: If printout of all sent and received
        data should be done.

    """

    def __init__(self, address, backend='pygatt', timeout=10.0, debug=False):
        """Constructor."""
        self._address = address
        self._debug = debug
        self._initialized = False

        if self._debug:
            print("Creating MetaWearClient for {0}...".format(address))

        if backend == 'pygatt':
            if PyGattBackend is None:
                raise PyMetaWearException(
                    "Need to install pygatt[GATTTOOL] package to use this backend.")
            self._backend = PyGattBackend(
                self._address, timeout=timeout, debug=debug)
        elif backend == 'pybluez':
            if PyBluezBackend is None:
                raise PyMetaWearException(
                    "Need to install pybluez[ble] package to use this backend.")
            self._backend = PyBluezBackend(
                self._address, timeout=timeout, debug=debug)
        elif backend == 'bluepy':
            if BluepyBackend is None:
                raise PyMetaWearException(
                    "Need to install bluepy package to use this backend.")
            self._backend = BluepyBackend(
                self._address, timeout=timeout, debug=debug)
        else:
            raise PyMetaWearException("Unknown backend: {0}".format(backend))

        if self._debug:
            print("Waiting for MetaWear board to be fully initialized...")

        while (not self.backend.initialized) and (not
                libmetawear.mbl_mw_metawearboard_is_initialized(self.board)):
            self.backend.sleep(0.1)

        self.firmware_version = tuple(
            [int(x) for x in self.backend.read_gatt_char_by_uuid(
            specs.DEV_INFO_FIRMWARE_CHAR[1]).decode().split('.')])
        self.model_version = int(self.backend.read_gatt_char_by_uuid(
            specs.DEV_INFO_MODEL_CHAR[1]).decode())

        # Initialize module classes.
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
        self.haptic = modules.HapticModule(self.board, debug=self._debug)
        self.led = modules.LEDModule(self.board, debug=self._debug)

    def __str__(self):
        return "MetaWearClient, {0}".format(self._address)

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

    def disconnect(self):
        """Disconnects this client from the MetaWear board."""
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
