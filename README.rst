**PyMetaWear is a community developed Python SDK started by** `Henrik Blidh <https://github.com/hbldh>`_ **.**  

**MbientLab does not provide support for this SDK and recommends that developers use the official Python SDK (https://github.com/mbientlab/MetaWear-SDK-Python) in case that is desired.**

==========
PyMetaWear
==========

Python package for connecting to and using
`MbientLab's MetaWear <https://mbientlab.com/>`_ boards.

PyMetaWear was previously a wrapper around the
`MetaWear C++ API <https://github.com/mbientlab/Metawear-CppAPI>`_,
providing a more Pythonic interface. In version 0.9.0 it instead becomes
a wrapper around `MetaWear's official Python SDK <https://github.com/mbientlab/MetaWear-SDK-Python>`_,
doing the very same thing. The official SDK handles the actual board
connections and communication while PyMetaWear aims to remove the low level
feeling of interacting with the MetaWear board.

**PyMetaWear is Linux-only**! 
Please use the other APIs for other platforms including Android, Windows, and Apple OS.

Installation
------------

Due to a dependency on ``gattlib``, a Python BLE package that is
poorly maintained, MbientLab has `forked it <https://github.com/mbientlab/pygattlib>`
and ships a patched version with its Python SDK. This makes installation of
PyMetaWear a bit messier:

.. code-block:: bash

    $ pip install git+https://github.com/mbientlab/pygattlib.git@master#egg=gattlib-0.20171002
    $ pip install pymetawear

Please ensure that the `dependencies <https://bitbucket.org/OscarAcena/pygattlib/src/a858e8626a93cb9b4ad56f3fb980a6517a0702c6/DEPENDS?at=default&fileviewer=file-view-default>`_ for ``gattlib`` are fulfilled before installing.


Development
~~~~~~~~~~~

TBW.

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

An example: blinking with the LED lights can be done like this with the
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

Actual addresses to your MetaWear board can be found by scanning, either
directly with ``hcitool lescan`` or with the included ``discover_devices`` method:

.. code-block:: python

    from pymetawear.client import discover_devices
    out = discover_devices()
    print out
    [(u'DD:3A:7D:4D:56:F0', u'MetaWear'), (u'FF:50:35:82:3B:5A', u'MetaWear')]

See the examples folder for more examples on how to use the ``libmetawear``
library with this client.

Modules
~~~~~~~
All functionality of the MetaWear C++ API is able to be used using the
PyMetaWear client, and some of the modules have had convenience methods
added to simplify the use of them. Below are two list, one of modules which
have had their convenience methods written and one of modules that are
awaiting such focus.

================= =============== =====================
Completed Modules Partial Modules Unimplemented Modules
================= =============== =====================
Accelerometer     GPIO            NeoPixel
Gyroscope                         Color Detector
Haptic                            Humidity
Switch                            iBeacon 
LED                               I2C
Barometer                         
Magnetometer                      
Temperature
Settings
Ambient Light
================= =============== =====================
