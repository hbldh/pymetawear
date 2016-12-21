#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:mod:`battery`
==================

Created by hbldh <henrik.blidh@nedomkull.com>
Created on 2016-04-02

"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import time
from math import atan2, pi

import matplotlib.pylot as plt

from pymetawear.discover import select_device
from pymetawear.client import MetaWearClient


class ComplimentaryFilter(object):

    def __init__(self, k, f, ):
        self.k = k
        self.frequency = f
        self._dt = 1.0 / self.frequency

        self._acc_data_added = False
        self._gyro_data_added = False

        self.raw_acc_data = []
        self.raw_gyro_data = []
        self.unfiltered_data = []
        self.filtered_data = []
        self.filtered_data_timestamps = []

    def get_pitch_roll_from_accelerometer(self, acc):
        pitch = atan2(acc[1], acc[2]) * 180 / pi
        roll = atan2(acc[0], acc[2]) * 180 / pi
        return pitch, roll

    def update_angle(self, acc, gyro):
        old_pitch, old_roll = self.filtered_data[-1]
        acc_pitch, acc_roll = self.get_pitch_roll_from_accelerometer(acc)
        self.unfiltered_data.append((acc_pitch, acc_roll))
        new_pitch = self.k * (old_pitch + gyro[0] * self._dt) + (1 - self.k) * acc_pitch
        new_roll = self.k * (old_roll + gyro[1] * self._dt) + (1 - self.k) * acc_roll
        return new_pitch, new_roll

    def add_accelerometer_data(self, data):
        if not self.raw_acc_data:
            self.filtered_data.append(self.get_pitch_roll_from_accelerometer(data[1]))
        self.raw_acc_data.append(data)
        self._acc_data_added = True
        if self._acc_data_added and self._gyro_data_added:
            self._acc_data_added = False
            self._gyro_data_added = False
            self.filtered_data.append(self.update_angle(
                self.raw_acc_data[-1][1], self.raw_gyro_data[-1][1]))
            self.filtered_data_timestamps.append(self.raw_acc_data[-1][0])

    def add_gyroscope_data(self, data):
        self.raw_gyro_data.append(data)
        self._gyro_data_added = True
        if self._acc_data_added and self._gyro_data_added:
            self._acc_data_added = False
            self._gyro_data_added = False
            self.filtered_data.append(self.update_angle(
                self.raw_acc_data[-1][1], self.raw_gyro_data[-1][1]))
            self.filtered_data_timestamps.append(self.raw_gyro_data[-1][0])


def run():
    address = select_device()
    c = MetaWearClient(str(address), 'pygatt', timeout=10, debug=False)
    print("New client created: {0}".format(c))
    f = ComplimentaryFilter(0.90, 50)

    print("Write accelerometer settings...")
    c.accelerometer.set_settings(data_rate=50.0, data_range=4.0)
    c.gyroscope.set_settings(data_rate=50.0, data_range=500.0)
    print("Subscribing to accelerometer signal notifications...")
    c.accelerometer.high_frequency_stream = False
    c.accelerometer.notifications(f.add_accelerometer_data)
    c.gyroscope.notifications(f.add_gyroscope_data)
    time.sleep(20.0)

    print("Unsubscribe to notification...")
    c.accelerometer.notifications(None)
    c.gyroscope.notifications(None)

    c.disconnect()

    ax = plt.subplot(211)
    ax.plot(f.filtered_data_timestamps, [x[0] for x in f.filtered_data])
    ax.plot(f.filtered_data_timestamps, [x[0] for x in f.unfiltered_data])

    return f


#c.disconnect()
