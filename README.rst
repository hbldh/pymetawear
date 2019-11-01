==========
PyMetaWear
==========

.. image:: https://img.shields.io/pypi/v/pymetawear
    :target: https://pypi.org/project/pymetawear/

.. image:: https://img.shields.io/pypi/l/pymetawear
    :alt: PyPI - License

.. image:: https://dev.azure.com/hbldh/github/_apis/build/status/hbldh.pymetawear?branchName=master
    :target: https://dev.azure.com/hbldh/github/_build/latest?definitionId=1?branchName=master

.. image:: https://coveralls.io/repos/github/hbldh/pymetawear/badge.svg?branch=master
    :target: https://coveralls.io/github/hbldh/pymetawear?branch=master

**PyMetaWear is a community developed Python SDK started by**
`Henrik Blidh <https://github.com/hbldh>`_ **. MbientLab does not provide support for this SDK.**

Python package for connecting to and using
`MbientLab's MetaWear <https://mbientlab.com/>`_ boards.

PyMetaWear can, from version 0.11.0, be used from both Windows and Linux. This is thanks to that the
``metawear`` `package <https://github.com/mbientlab/MetaWear-SDK-Python>`_ package is now depending on a
new BLE library called `PyWarble <https://github.com/mbientlab/PyWarble>`_ instead of ``gattlib``.
See installation instructions for more details about how to make it build on Windows.

Capabilities and Limitations
----------------------------

PyMetaWear was previously a wrapper around the
`MetaWear C++ API <https://github.com/mbientlab/Metawear-CppAPI>`_,
providing a more Pythonic interface. In version 0.9.0 it instead becomes
a wrapper around `MetaWear's official Python SDK <https://github.com/mbientlab/MetaWear-SDK-Python>`_,
doing the very same thing. The official SDK handles the actual board
connections and communication while PyMetaWear aims to remove the low level
feeling of interacting with the MetaWear board.


Installation
------------

.. code-block:: bash

    $ pip install pymetawear

Since version 0.11.0, the installation requirements for ``pymetawear`` has changed. See
`documentation <https://hbldh.github.io/pymetawear/>`_ for details on requirements for Linux and Windows respectively.

Documentation
-------------

Available in the `Github pages <https://hbldh.github.io/pymetawear/>`_ of this repository.

Basic Usage
-----------

The MetaWear client can be used in two ways: either as Pythonic
convenience class for handling a MetaWear board or as
a simple communication client governed by the ``libmetawear`` C++ library.

Creating a client, and thus also setting up a Bluetooth connection to the
MetaWear board, is equal for both the two usage profiles:

.. code-block:: python

    from pymetawear.client import MetaWearClient
    c = MetaWearClient('DD:3A:7D:4D:56:F0')

Example
~~~~~~~

Blinking with the LED lights can be done like this with the
convenience methods:

.. code-block:: python

    pattern = c.led.load_preset_pattern('blink', repeat_count=10)
    c.led.write_pattern(pattern, 'g')
    c.led.play()

or like this using the raw ``libmetawear`` shared library:

.. code-block:: python

    from ctypes import byref
    from pymetawear import libmetawear
    from mbientlab.metawear.cbindings import LedColor, LedPreset

    pattern = Led.Pattern(repeat_count=10)
    libmetawear.mbl_mw_led_load_preset_pattern(byref(pattern), LedPreset.BLINK)
    libmetawear.mbl_mw_led_write_pattern(c.board, byref(pattern), LedColor.GREEN)
    libmetawear.mbl_mw_led_play(c.board)

Bluetooth Low Energy Scanning
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Actual addresses to your MetaWear board can be found by scanning with the included ``discover_devices`` method:

.. code-block:: python

    from pymetawear.discover import discover_devices
    out = discover_devices()
    print(out)
    [(u'DD:3A:7D:4D:56:F0', u'MetaWear'), (u'FF:50:35:82:3B:5A', u'MetaWear')]

See the examples folder for more examples on how to use the ``libmetawear``
library with this client.

Modules
+++++++

All functionality of the MetaWear C++ API is able to be used using the
PyMetaWear client, and some of the modules have had convenience methods
added to simplify the use of them. Below is a list of modules which
have had their convenience methods written and one of modules that are
awaiting such focus.

================= =====================
Completed Modules Unimplemented Modules
================= =====================
Accelerometer     GPIO
Gyroscope         NeoPixel
Haptic            Color Detector
Switch            Humidity
LED               iBeacon
Barometer         I2C
Magnetometer
Temperature
Settings
Ambient Light
================= =====================
