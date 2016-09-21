#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:mod:`modules`
==================

Created by hbldh <henrik.blidh@nedomkull.com>
Created on 2016-04-14

"""

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import

from .base import PyMetaWearModule, Modules
from .accelerometer import AccelerometerModule
from .ambientlight import AmbientLightModule
from .barometer import BarometerModule
from .battery import BatteryModule
from .gyroscope import GyroscopeModule
from .haptic import HapticModule
from .led import LEDModule
from .magnetometer import MagnetometerModule
from .switch import SwitchModule
from .temperature import TemperatureModule
