#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""

.. moduleauthor:: mgeorgi <marcus.georgi@kinemic.de>

Created: 2016-02-01

"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import time
import logging
from functools import wraps
from ctypes import cast, POINTER

from pymetawear import libmetawear
from pymetawear.exceptions import PyMetaWearException
from mbientlab.metawear.cbindings import SensorFusionAccRange, \
    SensorFusionData, SensorFusionGyroRange, SensorFusionMode, \
    SensorOrientation, DataTypeId, CartesianFloat, CorrectedCartesianFloat, \
    Quaternion, EulerAngles, FnVoid_VoidP, FnVoid_DataP, TimeMode
from pymetawear.modules.base import PyMetaWearModule, Modules

log = logging.getLogger(__name__)
current_processor = None
waiting_for_processor = False
max_processor_wait_time = 5


def require_fusion_module(f):
    def wrapper(*args, **kwargs):
        if getattr(args[0], 'available', False) is False:
            raise PyMetaWearException("There is no Sensor Fusion "
                                      "module on your MetaWear board!")
        return f(*args, **kwargs)

    return wrapper


class SensorFusionModule(PyMetaWearModule):
    """MetaWear accelerometer module implementation.

    :param ctypes.c_long board: The MetaWear board pointer value.
    :param int module_id: The module id of the sensorfusion
        component, obtained from ``libmetawear``.
    :param bool debug: If ``True``, module prints out debug information.

    """

    def __init__(self, board, module_id, debug=False):
        super(SensorFusionModule, self).__init__(board, debug)
        self.module_id = module_id

        if self.module_id == Modules.MBL_MW_MODULE_NA:
            # No sensor fusion present!
            self.available = False
        else:
            self.available = True

        self.board = board

        self.current_active_signal = None

        self._streams_to_enable = {
            SensorFusionData.CORRECTED_ACC: False,
            SensorFusionData.CORRECTED_GYRO: False,
            SensorFusionData.CORRECTED_MAG: False,
            SensorFusionData.QUATERION: False,
            SensorFusionData.EULER_ANGLE: False,
            SensorFusionData.GRAVITY_VECTOR: False,
            SensorFusionData.LINEAR_ACC: False,
        }

        self._data_source_signals = {
            SensorFusionData.CORRECTED_ACC: None,
            SensorFusionData.CORRECTED_GYRO: None,
            SensorFusionData.CORRECTED_MAG: None,
            SensorFusionData.QUATERION: None,
            SensorFusionData.EULER_ANGLE: None,
            SensorFusionData.GRAVITY_VECTOR: None,
            SensorFusionData.LINEAR_ACC: None,
        }

        self._callbacks = {}
        self._waiting_for_processor = False

        if debug:
            log.setLevel(logging.DEBUG)

    def __str__(self):
        return "{0}".format(self.module_name)

    def __repr__(self):
        return str(self)

    @require_fusion_module
    def set_sample_delay(self, data_source, delay=None, differential=False):
        """
        Change the delay between samples using the onboard time processor
        module to change the effective sampling rate of a specific data source.

        :param data_source: A data source from sensor.SensorFusion
        :param delay: The delay in ms between samples,
            or None to reset to default
        :param differential: Set Time Preprocessor mode to differential,
            instead of the default, absolute
        """

        global current_processor
        global waiting_for_processor

        if self._data_source_signals[data_source] is None:
            log.debug("Getting data signal for data source {0}".format(
                data_source
            ))
            self._data_source_signals[data_source] = \
                libmetawear.mbl_mw_sensor_fusion_get_data_signal(
                    self.board, data_source
                )

        if delay is not None:
            mode = TimeMode.DIFFERENTIAL if differential else \
                TimeMode.ABSOLUTE
            waiting_for_processor = True
            log.debug("Creating time dataprocessor for signal {0}".format(
                self._data_source_signals[data_source]
            ))
            libmetawear.mbl_mw_dataprocessor_time_create(
                self._data_source_signals[data_source],
                mode,
                delay,
                FnVoid_VoidP(processor_set))

            wait_time = 0
            while waiting_for_processor and wait_time < max_processor_wait_time:
                sleeptime = 0.1
                time.sleep(sleeptime)
                wait_time += sleeptime
            if current_processor is not None:
                self._data_source_signals[data_source] = current_processor
                current_processor = None
            else:
                raise PyMetaWearException("Can't set data processor!")

        else:
            data_signal = libmetawear.mbl_mw_sensor_fusion_get_data_signal(
                    self.board, data_source)
            if self._data_source_signals[data_source] != data_signal:
                libmetawear.mbl_mw_dataprocessor_remove(
                    self._data_source_signals[data_source]
                )
                self._data_source_signals[data_source] = data_signal

    def _delay_set(self, processor):
        self._current_processor = processor
        self._waiting_for_processor = False

    @require_fusion_module
    def set_mode(self, mode):
        libmetawear.mbl_mw_sensor_fusion_set_mode(self.board,
                                                  mode)
        libmetawear.mbl_mw_sensor_fusion_write_config(self.board)

    @require_fusion_module
    def set_acc_range(self, acc_range):
        libmetawear.mbl_mw_sensor_fusion_set_acc_range(self.board,
                                                       acc_range)
        libmetawear.mbl_mw_sensor_fusion_write_config(self.board)

    @require_fusion_module
    def set_gyro_range(self, gyro_range):
        libmetawear.mbl_mw_sensor_fusion_set_gyro_range(self.board,
                                                        gyro_range)
        libmetawear.mbl_mw_sensor_fusion_write_config(self.board)

    @require_fusion_module
    def get_data_signal(self, data_source):
        if self._data_source_signals[data_source] is None:
            self._data_source_signals[data_source] = \
                libmetawear.mbl_mw_sensor_fusion_get_data_signal(
                    self.board, data_source
                )
        return self._data_source_signals[data_source]

    @property
    def data_signal(self):
        return self.current_active_signal

    @property
    def module_name(self):
        return "Sensor Fusion"

    def get_current_settings(self):
        raise NotImplementedError()

    def get_possible_settings(self):
        raise NotImplementedError()

    def set_settings(self):
        raise NotImplementedError()

    @require_fusion_module
    def notifications(self,
                      corrected_acc_callback=None,
                      corrected_gyro_callback=None,
                      corrected_mag_callback=None,
                      quaternion_callback=None,
                      euler_angle_callback=None,
                      gravity_callback=None,
                      linear_acc_callback=None):
        """Subscribe or unsubscribe to sensor fusion notifications.

        Convenience method for handling sensor fusion usage.

        Example:

        .. code-block:: python

            def handle_notification(data):
                # Handle a (epoch_time, (x,y,z,accuracy)) corrected acc tuple.
                epoch = data[0]
                xyzaccu = data[1]
                print("[{0}] X: {1}, Y: {2}, Z: {3}".format(
                    epoch, *xyzaccu[:-1]))

            mwclient.sensorfusion.notifications(
                corrected_acc_callback=handle_notification)

        :param callable corrected_acc_callback: Acceleration notification
            callback function.
            If `None`, unsubscription to acceleration notifications is
            registered.
        :param callable corrected_gyro_callback: Gyroscope notification
            callback function.
            If `None`, unsubscription to gyroscope notifications is registered.
        :param callable corrected_mag_callback: Magnetometer notification
            callback function.
            If `None`, unsubscription to magnetometer notifications is
            registered.
        :param callable quaternion_callback: Quaternion notification callback
            function.
            If `None`, unsubscription to quaternion notifications is registered.
        :param callable euler_angle_callback: Euler angle notification callback
            function.
            If `None`, unsubscription to euler angle notifications is
            registered.
        :param callable gravity_callback: Gravity vector notification callback
            function.
            If `None`, unsubscription to gravity notifications is registered.
        :param callable linear_acc_callback: Linear acceleration notification
            callback function.
            If `None`, unsubscription to linear acceleration notifications is
            registered.

        """
        callback_data_source_map = {
            SensorFusionData.CORRECTED_ACC: corrected_acc_callback,
            SensorFusionData.CORRECTED_GYRO: corrected_gyro_callback,
            SensorFusionData.CORRECTED_MAG: corrected_mag_callback,
            SensorFusionData.QUATERION: quaternion_callback,
            SensorFusionData.EULER_ANGLE: euler_angle_callback,
            SensorFusionData.GRAVITY_VECTOR: gravity_callback,
            SensorFusionData.LINEAR_ACC: linear_acc_callback
        }

        for data_source in callback_data_source_map:
            if callback_data_source_map[data_source] is not None:
                self._streams_to_enable[data_source] = True
            else:
                self._streams_to_enable[data_source] = False

        enable = False in [x is None for x in callback_data_source_map.values()]
        log.debug("Enable: %s" % enable)

        if not enable:
            self.stop()
            self.toggle_sampling(False)

        for data_source in callback_data_source_map:
            self.current_active_signal = self.get_data_signal(data_source)
            callback = callback_data_source_map[data_source]
            if callback is not None:
                self.check_and_change_callback(
                    self.get_data_signal(data_source),
                    sensor_data(callback)
                )
            else:
                self.check_and_change_callback(
                    self.get_data_signal(data_source),
                    None
                )

        if enable:
            self.toggle_sampling(True)
            self.start()

    def check_and_change_callback(self, data_signal, callback):
        if callback is not None:
            if self._debug:
                log.debug("Subscribing to {0} changes. (Sig#: {1})".format(
                    self.module_name, data_signal))
            if data_signal in self._callbacks:
                raise PyMetaWearException(
                    "Subscription to {0} signal already in place!")
            self._callbacks[data_signal] = (callback, FnVoid_DataP(callback))
            libmetawear.mbl_mw_datasignal_subscribe(
                data_signal, self._callbacks[data_signal][1])
        else:
            if data_signal not in self._callbacks:
                return
            if self._debug:
                log.debug("Unsubscribing to {0} changes. (Sig#: {1})".format(
                    self.module_name, data_signal))
            libmetawear.mbl_mw_datasignal_unsubscribe(data_signal)
            del self._callbacks[data_signal]

    @require_fusion_module
    def start(self):
        """Switches the sensorfusion to active mode."""
        libmetawear.mbl_mw_sensor_fusion_start(self.board)

    @require_fusion_module
    def stop(self):
        """Switches the sensorfusion to standby mode."""
        libmetawear.mbl_mw_sensor_fusion_stop(self.board)

    @require_fusion_module
    def toggle_sampling(self, enabled=True):
        """Enables or disables sensor fusion sampling.

        :param bool enabled: Desired state of the sensor fusion module.

        """
        if enabled:
            for data_source in self._streams_to_enable:
                if self._streams_to_enable[data_source]:
                    libmetawear.mbl_mw_sensor_fusion_enable_data(
                        self.board, data_source)
        else:
            libmetawear.mbl_mw_sensor_fusion_clear_enabled_mask(
                self.board)


def processor_set(processor):
    """
    Set global variables as the libmetawear callback can't handle the self
    parameter of instance methods.

    :param processor: The processor thas was created
    """
    global current_processor
    global waiting_for_processor
    current_processor = processor
    waiting_for_processor = False


def sensor_data(func):
    @wraps(func)
    def wrapper(data):
        if data.contents.type_id == DataTypeId.CARTESIAN_FLOAT:
            epoch = int(data.contents.epoch)
            data_ptr = cast(data.contents.value, POINTER(CartesianFloat))
            func((epoch, (data_ptr.contents.x,
                          data_ptr.contents.y,
                          data_ptr.contents.z)))
        elif data.contents.type_id == DataTypeId.QUATERNION:
            epoch = int(data.contents.epoch)
            data_ptr = cast(data.contents.value, POINTER(Quaternion))
            func((epoch, (data_ptr.contents.w,
                          data_ptr.contents.x,
                          data_ptr.contents.y,
                          data_ptr.contents.z)))
        elif data.contents.type_id == DataTypeId.CORRECTED_CARTESIAN_FLOAT:
            epoch = int(data.contents.epoch)
            data_ptr = cast(data.contents.value,
                            POINTER(CorrectedCartesianFloat))
            func((epoch, (data_ptr.contents.x,
                          data_ptr.contents.y,
                          data_ptr.contents.z,
                          data_ptr.contents.accuracy)))
        elif data.contents.type_id == DataTypeId.EULER_ANGLE:
            epoch = int(data.contents.epoch)
            data_ptr = cast(data.contents.value, POINTER(EulerAngles))
            func((epoch, (data_ptr.contents.heading,
                          data_ptr.contents.pitch,
                          data_ptr.contents.roll,
                          data_ptr.contents.yaw)))
        else:
            raise PyMetaWearException('Incorrect data type id: {0}'.format(
                data.contents.type_id))

    return wrapper
