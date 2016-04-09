#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""

.. moduleauthor:: hbldh <henrik.blidh@nedomkull.com>
Created on 2016-04-01

"""

from __future__ import division
from __future__ import print_function
# from __future__ import unicode_literals
from __future__ import absolute_import

import re
import uuid

from pymetawear.mbientlab.metawear import sensor


def _high_low_2_uuid(uuid_high, uuid_low):
    """Combine high and low bits of a split UUID.

    :param uuid_high: The high 64 bits of the UUID.
    :type uuid_high: int
    :param uuid_low: The low 64 bits of the UUID.
    :type uuid_low: int
    :return: The UUID.
    :rtype: :py:class:`uuid.UUID`

    """
    return uuid.UUID(int=(uuid_high << 64) + uuid_low)


# Service specs obtained from connection.h
METAWEAR_SERVICE_NOTIFY_CHAR = _high_low_2_uuid(0x326a900085cb9195,
                                                0xd9dd464cfbbae75a), \
                               _high_low_2_uuid(0x326a900685cb9195,
                                                0xd9dd464cfbbae75a)


# Service & char specs obtained from metawearboard.cpp

_DEVICE_INFO_SERVICE = _high_low_2_uuid(0x0000180a00001000, 0x800000805f9b34fb)

METAWEAR_COMMAND_CHAR = METAWEAR_SERVICE_NOTIFY_CHAR, \
                        _high_low_2_uuid(0x326a900185cb9195, 0xd9dd464cfbbae75a)
DEV_INFO_FIRMWARE_CHAR = _DEVICE_INFO_SERVICE, \
                         _high_low_2_uuid(0x00002a2600001000,
                                          0x800000805f9b34fb)
DEV_INFO_MODEL_CHAR = _DEVICE_INFO_SERVICE, \
                      _high_low_2_uuid(0x00002a2400001000, 0x800000805f9b34fb)

class Modules(object):

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
    MBL_MW_MODULE_DEBUG = 0xfe


class AccelerometerSpecs(object):
    def __init__(self, module_id):

        acc_sensors = [
            sensor.AccelerometerBmi160,
            sensor.AccelerometerBma255,
            sensor.AccelerometerMma8452q
        ]
        for a in acc_sensors:
            if getattr(a, 'MODULE_TYPE', -1) == module_id:
                self.acc_class = a

        if self.acc_class is not None:
            # Parse possible output data rates for this accelerometer.
            self.odr = {".".join(re.search(
                '^ODR_([0-9]+)\_*([0-9]*)HZ', k).groups()):
                            getattr(self.acc_class, k, None) for k in filter(
                lambda x: x.startswith('ODR'), vars(self.acc_class))}

            # Parse possible output data ranges for this accelerometer.
            if len(list(filter(lambda x: x.startswith('FSR'),
                               vars(self.acc_class)))) == 0:
                acc_class = sensor.AccelerometerBosch
            else:
                acc_class = self.acc_class
            self.fsr = {int(re.search('^FSR_([0-9]+)G', k).groups()[0]):
                            getattr(acc_class, k, None) for k in
                        filter(lambda x: x.startswith('FSR'), vars(acc_class))}

    def __str__(self):
        return "Accelerometer {0}: Data rates (Hz): {1}, Data ranges (g): {2}".format(
            self.acc_class.__name__.replace('Accelerometer', ''),
            [float(k) for k in sorted(self.odr.keys(),
                                      key=lambda x:(float(x)))],
            [k for k in sorted(self.fsr.keys())])

    def __repr__(self):
        return str(self)

    def get_odr(self, value):
        sorted_ord_keys = sorted(self.odr.keys(), key=lambda x:(float(x)))
        diffs = [abs(value - float(k)) for k in sorted_ord_keys]
        min_diffs = min(diffs)
        if min_diffs > 0.5:
            raise ValueError("Requested ODR ({0}) was not part of "
                             "possible values: {1}".format(
                value, [float(x) for x in sorted_ord_keys]))
        return self.odr.get(sorted_ord_keys[diffs.index(min_diffs)])

    def get_fsr(self, value):
        fsr = self.fsr.get(value, None)
        if fsr is None:
            raise ValueError("Requested FSR ({0}) was not part of "
                             "possible values: {1}".format(
                value, [x for x in sorted(self.fsr.keys())]))
        return fsr
