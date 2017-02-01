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
from pymetawear.mbientlab.metawear.sensor import SensorFusion

address = select_device()
c = MetaWearClient(str(address), 'pygatt', debug=True)
print("New client created: {0}".format(c))

def handle_quat(data):
    # Handle a (epoch_time, (w,x,y,z)) quaternion tuple.¬
    epoch = data[0]
    xyzaccu = data[1]
    print("[{0}] W {1}, X {2}, Y {3}, Z {4}".format(epoch, *xyzaccu))

def handle_notification(data):
    # Handle a (epoch_time, (x,y,z,accuracy)) corrected acc¬
    # tuple.¬
    epoch = data[0]
    xyzaccu = data[1]
    print("[{0}] X: {1}, Y: {2}, Z: {3}".format(epoch, *xyzaccu[:-1]))

def handle_euler(data):
    # Handle a (epoch_time, (heading,pitch,roll,yaw)) euler angle tuple.¬
    epoch = data[0]
    xyzaccu = data[1]
    print("[{0}] Heading: {1}, Pitch: {2}, Roll: {3}, Yaw: {4}".format(
        epoch, *xyzaccu))


print("Write Sensor Fusion settings...")
c.sensorfusion.set_mode(SensorFusion.MODE_NDOF)
c.sensorfusion.set_acc_range(SensorFusion.ACC_RANGE_8G)
c.sensorfusion.set_gyro_range(SensorFusion.GYRO_RANGE_1000DPS)
print("Subscribing to Sensor Fusion Quaternion signal notifications...")
c.sensorfusion.notifications(quaternion_callback=handle_quat)
#c.sensorfusion.notifications(euler_angle_callback=handle_euler)
#c.sensorfusion.notifications(corrected_acc_callback=handle_notification)

time.sleep(20.0)

print("Unsubscribe to notification...")
c.sensorfusion.notifications()

time.sleep(5.0)

c.disconnect()
