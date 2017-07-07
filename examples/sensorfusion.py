#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:mod:`sensorfusion`
==================

Created by mgeorgi <marcus.georgi@kinemic.de>
Created on 2016-02-01

"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import time

from pymetawear.discover import select_device
from pymetawear.client import MetaWearClient
from pymetawear.mbientlab.metawear.cbindings import SensorFusionData, SensorFusionGyroRange, SensorFusionAccRange, SensorFusionMode

address = select_device()
c = MetaWearClient(str(address), 'pygatt', debug=True)
print("New client created: {0}".format(c))

def handle_quat(data):
    # Handle a (epoch_time, (w,x,y,z)) quaternion tuple.¬
    epoch = data[0]
    xyzaccu = data[1]
    print("QUAT [{0}] W {1}, X {2}, Y {3}, Z {4}".format(epoch, *xyzaccu))

def handle_notification(data):
    # Handle a (epoch_time, (x,y,z,accuracy)) corrected acc¬
    # tuple.¬
    epoch = data[0]
    xyzaccu = data[1]
    print("ACC [{0}] X: {1}, Y: {2}, Z: {3}".format(epoch, *xyzaccu[:-1]))

def handle_gyro(data):
    # Handle a (epoch_time, (x,y,z,accuracy)) corrected gyro¬
    # tuple.¬
    epoch = data[0]
    xyzaccu = data[1]
    print("GYRO [{0}] X: {1}, Y: {2}, Z: {3}".format(epoch, *xyzaccu[:-1]))

def handle_euler(data):
    # Handle a (epoch_time, (heading,pitch,roll,yaw)) euler angle tuple.¬
    epoch = data[0]
    xyzaccu = data[1]
    print("EULER [{0}] Heading: {1}, Pitch: {2}, Roll: {3}, Yaw: {4}".format(
        epoch, *xyzaccu))


print("Write Sensor Fusion settings...")
c.sensorfusion.set_mode(SensorFusionMode.NDOF)
c.sensorfusion.set_acc_range(SensorFusionAccRange._8G)
c.sensorfusion.set_gyro_range(SensorFusionGyroRange._1000DPS)

print("Set Time Processor to limit data rate to 50Hz for each channel")
#c.sensorfusion.set_sample_delay(SensorFusionData.EULER_ANGLE, 20)
c.sensorfusion.set_sample_delay(SensorFusionData.QUATERION, 20)
#c.sensorfusion.set_sample_delay(SensorFusionData.CORRECTED_ACC, 20)
#c.sensorfusion.set_sample_delay(SensorFusionData.CORRECTED_GYRO, 20)

print("Subscribing to Sensor Fusion Quaternion signal notifications...")
#c.sensorfusion.notifications(euler_angle_callback=handle_euler)
c.sensorfusion.notifications(quaternion_callback=handle_quat)
#c.sensorfusion.notifications(corrected_acc_callback=handle_notification,
#                             quaternion_callback=handle_quat,
#                             corrected_gyro_callback=handle_gyro)

time.sleep(10.0)

print("Unsubscribe to notification...")
c.sensorfusion.notifications()

time.sleep(5.0)

c.disconnect()
