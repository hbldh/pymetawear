#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Base module
-----------

Created by hbldh <henrik.blidh@nedomkull.com> on 2016-04-14
Modified by lkasso <hello@mbientlab.com>

"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import logging
from copy import deepcopy
from ctypes import c_int, c_uint, c_float, cast, POINTER, c_ubyte, byref
from functools import wraps
from threading import Event

from pymetawear import libmetawear
from pymetawear.exceptions import PyMetaWearException, PyMetaWearDownloadTimeout
from mbientlab.metawear.cbindings import FnVoid_DataP, DataTypeId, \
    CartesianFloat, BatteryState, Tcs34725ColorAdc, EulerAngles, \
    Quaternion, CorrectedCartesianFloat, FnVoid_VoidP, \
    LogDownloadHandler, FnVoid_UInt_UInt, FnVoid_UByte_Long_UByteP_UByte

log = logging.getLogger(__name__)


class Modules(object):
    """Class for storing PyMetaWear module identifiers."""

    MBL_MW_MODULE_NA = -1
    MBL_MW_MODULE_SWITCH = 1
    MBL_MW_MODULE_LED = 2
    MBL_MW_MODULE_ACCELEROMETER = 3
    MBL_MW_MODULE_TEMPERATURE = 4
    MBL_MW_MODULE_GPIO = 5
    MBL_MW_MODULE_NEO_PIXEL = 6
    MBL_MW_MODULE_IBEACON = 7
    MBL_MW_MODULE_HAPTIC = 8
    MBL_MW_MODULE_DATA_PROCESSOR = 9
    MBL_MW_MODULE_EVENT = 0xa
    MBL_MW_MODULE_LOGGING = 0xb
    MBL_MW_MODULE_TIMER = 0xc
    MBL_MW_MODULE_I2C = 0xd
    MBL_MW_MODULE_MACRO = 0xf
    MBL_MW_MODULE_GSR = 0x10
    MBL_MW_MODULE_SETTINGS = 0x11
    MBL_MW_MODULE_BAROMETER = 0x12
    MBL_MW_MODULE_GYRO = 0x13
    MBL_MW_MODULE_AMBIENT_LIGHT = 0x14
    MBL_MW_MODULE_MAGNETOMETER = 0x15
    MBL_MW_MODULE_HUMIDITY = 0x16
    MBL_MW_MODULE_COLOR_DETECTOR = 0x17
    MBL_MW_MODULE_PROXIMITY = 0x18
    MBL_MW_MODULE_SENSOR_FUSION = 0x19
    MBL_MW_MODULE_DEBUG = 0xfe


class PyMetaWearModule(object):
    """Base class for PyMetaWear module implementations.

    :param ctypes.c_long board: The MetaWear board pointer value.
    :param bool debug: If ``True``, module prints out debug information.

    """

    def __init__(self, board, debug=False):
        self.board = board
        self._debug = debug
        self.is_present = True
        self.callback = None

        if debug:
            log.setLevel(logging.DEBUG)

    def __str__(self):
        return "PyMetaWearModule"

    def __repr__(self):
        return super(PyMetaWearModule, self).__repr__()

    @property
    def module_name(self):
        """Get module name.

        :return: The name of this module.
        :rtype: str

        """
        return ''

    @property
    def sensor_name(self):
        """Get sensor name, if applicable.

        :return: The name of this module.
        :rtype: str or None

        """
        return None

    @property
    def data_signal(self):
        """Returns the data signal pointer value for the switch module.

        :returns: The pointer value. (Long if on x64 architecture.)
        :rtype: :py:class:`ctypes.c_long` or :py:class:`ctypes.c_int`

        """
        raise PyMetaWearException(
            "No data signal exists for {0} module.".format(self))

    def set_settings(self, **kwargs):
        raise PyMetaWearException(
            "No settings exists for {0} module.".format(self))

    def get_current_settings(self):
        return {}

    def get_possible_settings(self):
        return {}

    def notifications(self, callback=None):
        """Toggle notifications/subscriptions to data signals
        on the MetaWear board.

        :param callable callback: The function to call when
            data signal notification arrives. If ``None``, an
            unsubscription to notifications is sent.

        """
        data_signal = self.data_signal
        if callback is not None:
            if self._debug:
                log.debug("Subscribing to {0} changes. (Sig#: {1})".format(
                    self.module_name, data_signal))
            if self.callback is not None:
                raise PyMetaWearException(
                    "Subscription to {0} signal already in place!")
            self.callback = (callback, FnVoid_DataP(callback))
            libmetawear.mbl_mw_datasignal_subscribe(
                data_signal, self.callback[1])
        else:
            if self._debug:
                log.debug("Unsubscribing to {0} changes. (Sig#: {1})".format(
                    self.module_name, data_signal))
            if self.callback is None:
                return
            libmetawear.mbl_mw_datasignal_unsubscribe(data_signal)
            self.callback = None


class PyMetaWearLoggingModule(PyMetaWearModule):
    """Special class with additions for sensors with logging support."""

    def __init__(self, board, debug=False):
        super(PyMetaWearLoggingModule, self).__init__(board, debug)

        self._logger_ready_event = None
        self.data_received = Event()
        self._download_done = False
        self._logger_running = False
        self._logger_address = None

        self._logged_data = []

    def _logger_ready(self, address):
        if address:
            self._logger_address = address
            if self._debug:
                log.debug("Logger address: {0}".format(self._logger_address))
        else:
            # Do nothing here. Let main thread handle lack of address.
            pass
        self._logger_ready_event.set()

    def _progress_update(self, entries_left, total_entries):
        log.info("Download Progress: {0} / {1}".format(
            total_entries - entries_left, total_entries))
        self.data_received.set()
        if entries_left == 0:
            self._download_done = True

    def _unknown_entry(self, id, epoch, data, length):
        """Handle unknown data entries in the log.

        I have no idea what this data is. Needs further investigation.
        Might work to parse data with this:

        from pymetawear.modules.base import DATA_HANDLERS, _error_handler
        DATA_HANDLERS.get(data.contents.type_id, _error_handler)(data)

        :param id (int):
        :param epoch (int):
        :param data:
        :param length (int):

        """
        if self._debug:
            log.debug('Unknown Entry: ID: {0}, epoch: {1}, '
                      'data: {2}, Length: {3}'.format(id, epoch, bytearray(data), length))

    def _unhandled_entry(self, data):
        if self._debug:
            log.debug('Unhandled Entry: ' + str(data))

    def _default_download_callback(self, data):
        if self._debug:
            log.debug(data)
        self._logged_data.append(deepcopy(data))

    def start(self):
        raise NotImplementedError("Must be implemented by module.")

    def stop(self):
        raise NotImplementedError("Must be implemented by module.")

    def toggle_sampling(self, enabled=True):
        raise NotImplementedError("Must be implemented by module.")

    def start_logging(self):
        """Setup and start logging of data signals on the MetaWear board"""
        data_signal = self.data_signal
        #if getattr(self, 'high_frequency_stream', default=False):
        #    raise PyMetaWearException("Cannot log on high frequency stream signal.")
        self._logger_ready_event = Event()
        logger_ready = FnVoid_VoidP(self._logger_ready)
        libmetawear.mbl_mw_datasignal_log(self.data_signal, logger_ready)
        self._logger_ready_event.wait()
        if self._logger_address is None:
            raise PyMetaWearException(
                'Failed to start logging for {0} module!'.format(
                    self.module_name))

        if self._debug:
            log.debug("Start Logger (Logger#: {0}, Signal#: {1})".format(
                self._logger_address, data_signal))

        self._logger_running = True
        self._download_done = False
        libmetawear.mbl_mw_logging_start(self.board, 0)
        self.toggle_sampling(True)
        self.start()

    def stop_logging(self):
        """Stop logging of data signals on the MetaWear board"""
        self.stop()
        self.toggle_sampling(False)
        if self._debug:
            log.debug("Stop Logger (Logger#: {0})".format(self._logger_address))

        libmetawear.mbl_mw_logging_stop(self.board)
        self._logger_running = False

    def download_log(
            self,
            timeout=5.0,
            data_callback=None,
            progress_update_function=None,
            unknown_entry_function=None,
            unhandled_entry_function=None
    ):
        """Download logged data from the MetaWear board

        :param data_callback: The function to call when
            downloaded data arrives.

        """
        if self._logger_running:
            # Stop logging if it is active.
            self.stop_logging()

        if data_callback is None:
            data_callback = self._default_download_callback
        if progress_update_function is None:
            progress_update_function = self._progress_update
        if unknown_entry_function is None:
            unknown_entry_function = self._unknown_entry
        if unhandled_entry_function is None:
            unhandled_entry_function = self._unhandled_entry

        data_point_handler = FnVoid_DataP(data_handler(data_callback))
        progress_update = FnVoid_UInt_UInt(progress_update_function)
        unknown_entry = FnVoid_UByte_Long_UByteP_UByte(unknown_entry_function)
        unhandled_entry = FnVoid_DataP(data_handler(unhandled_entry_function))
        log_download_handler = LogDownloadHandler(
            received_progress_update=progress_update,
            received_unknown_entry=unknown_entry,
            received_unhandled_entry=unhandled_entry
        )

        if self._debug:
            log.debug("Subscribe to Logger. (Logger#: {0})".format(
                self._logger_address))
        libmetawear.mbl_mw_logger_subscribe(
            self._logger_address, data_point_handler)

        if self._debug:
            log.debug("Waiting for completed download. (Logger#: {0})".format(
                self._logger_address))
        libmetawear.mbl_mw_logging_download(
            self.board, 100, byref(log_download_handler))

        while not self._download_done:
            status = self.data_received.wait(timeout)
            self.data_received = Event()
            if not status:
                raise PyMetaWearDownloadTimeout(
                    "Bluetooth connection lost! Please reconnect and retry download...")

        if self._debug:
            log.debug("Download done. (Logger#: {0})".format(
                self._logger_address))

        if self._debug:
            log.debug("Remove logger. (Logger#: {0})".format(
                self._logger_address))
        libmetawear.mbl_mw_logger_remove(self._logger_address)

        logged_data = self._logged_data
        self._logged_data = []

        return logged_data

        # status = False
        # while not self._download_done:
        #     if not status:
        #         time.sleep(0.2)
        #         client.mw.disconnect()
        #         client.mw.connect()
        #         if self._debug:
        #             log.debug("Subscribe to Logger. (Logger#: {0})".format(
        #                 self._logger_address))
        #         libmetawear.mbl_mw_logger_subscribe(self._logger_address,
        #                                             data_point_handler)
        #
        #         time.sleep(0.2)
        #         if self._debug:
        #             log.debug(
        #                 "Waiting for completed download. (Logger#: {0})".format(
        #                     self._logger_address))
        #         libmetawear.mbl_mw_logging_download(self.board, 100,
        #                                             byref(log_download_handler))
        #
        #     status = self.data_received.wait(10)
        #     if not status:
        #         print("BT connetion lost! Retry download...")
        #         client.mw.disconnect()
        #         client.mw.connect()
        #
        # if self._debug:
        #     log.debug("Download done. (Logger#: {0})".format(
        #         self._logger_address))
        #
        # time.sleep(0.2)
        # if self._debug:
        #     log.debug("Remove logger. (Logger#: {0})".format(
        #         self._logger_address))
        #     libmetawear.mbl_mw_logger_remove(self._logger_address)
        #
        # time.sleep(0.2)
        # if self._debug:
        #     log.debug("Cleanup memory. (Logger#: {0})".format(
        #         self._logger_address))
        #     libmetawear.mbl_mw_metawearboard_tear_down(self.board)


def _error_handler(data):
    raise RuntimeError('Unrecognized data type id: ' +
                       str(data.contents.type_id))


def _byte_array_handler(data):
    ptr = cast(data.contents.value, POINTER(c_ubyte * data.contents.length))
    return [ptr.contents[i].value for i in range(0, data.contents.length)]


DATA_HANDLERS = {
    DataTypeId.UINT32: lambda x: cast(
        x.contents.value, POINTER(c_uint)).contents.value,
    DataTypeId.INT32: lambda x: cast(
        x.contents.value, POINTER(c_int)).contents.value,
    DataTypeId.FLOAT: lambda x: cast(
        x.contents.value, POINTER(c_float)).contents.value,
    DataTypeId.CARTESIAN_FLOAT: lambda x: cast(
        x.contents.value, POINTER(CartesianFloat)).contents,
    DataTypeId.BATTERY_STATE: lambda x: cast(
        x.contents.value, POINTER(BatteryState)).contents,
    DataTypeId.BYTE_ARRAY: _byte_array_handler,
    DataTypeId.TCS34725_ADC: lambda x: cast(
        x.contents.value, POINTER(Tcs34725ColorAdc)).contents,
    DataTypeId.EULER_ANGLE: lambda x: cast(
        x.contents.value, POINTER(EulerAngles)).contents,
    DataTypeId.QUATERNION: lambda x: cast(
        x.contents.value, POINTER(Quaternion)).contents,
    DataTypeId.CORRECTED_CARTESIAN_FLOAT: lambda x: cast(
        x.contents.value, POINTER(CorrectedCartesianFloat)).contents
}


def data_handler(func):
    @wraps(func)
    def wrapper(data):
        func({
            'epoch': int(data.contents.epoch),
            'value': DATA_HANDLERS.get(
                data.contents.type_id, _error_handler)(data)
        })

    return wrapper
