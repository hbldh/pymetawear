**PyMetaWear is a community developed Python SDK started by** `Henrik Blidh <https://github.com/hbldh>`_ **.**  

**MbientLab does not provide support for this SDK and recommends that developers use the official Python SDK (https://github.com/mbientlab/MetaWear-SDK-Python) to receive up-to-date feature support for your MetaSensors.**  

==========
PyMetaWear
==========

Python package for connecting to and using
`MbientLab's MetaWear <https://mbientlab.com/>`_ boards.

PyMetawear is meant to be a thin wrapper around the
`MetaWear C++ API <https://github.com/mbientlab/Metawear-CppAPI>`_,
providing a more Pythonic interface. It has support for two different
Python packages for Bluetooth Low Energy communication:

- `pygatt <https://github.com/peplin/pygatt>`_
- `pybluez <https://github.com/karulis/pybluez>`_ with
  `gattlib <https://bitbucket.org/OscarAcena/pygattlib>`_

PyMetaWear can be run with Python 2 and 3.4 with both backends,
but only with the `pygatt` backend for Python 3.5.

**PyMetaWear is Linux-only**! 
Please use the other APIs for other platforms including Android, Windows, and Apple OS.

Installation
------------

Currently, the `pygatt <https://github.com/peplin/pygatt>`_ communication
backend is used by default.

Debian requirements for ``pygatt and pymetawear`` 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
* ``build-essential``
* ``python-dev``

.. code-block:: bash

    $ pip install pygatt 

Additional requirements for ``pybluez``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* ``libglib2.0-dev``
* ``bluetooth``
* ``libbluetooth-dev``
* ``libboost-python-dev``
* ``libboost-thread-dev``

.. code-block:: bash

    $ pip install pybluez[ble]

Development
~~~~~~~~~~~
Clone this repository and run

.. code-block:: bash

    $ python setup.py build

to pull in the `MetaWear C++ API <https://github.com/mbientlab/Metawear-CppAPI>`_ submodule,
build it and copy the Python wrappers from it to the PyMetaWear folder.

Documentation
-------------

New documentation coming soon.

Basic Usage
-----------

The MetaWear client can be used in two ways: either as Pythonic
convenience class for handling a MetaWear board or as
a simple communication client governed by the ``libmetawear`` C++ library.

Creating a client, and thus also setting up a Bluetooth connection to the
MetaWear board, is equal for both the two usage profiles:

.. code-block:: python

    from pymetawear.client import MetaWearClient
    backend = 'pygatt' # Or 'pybluez'
    c = MetaWearClient('DD:3A:7D:4D:56:F0', backend)

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
    from pymetawear.mbientlab.metawear.cbindings import LedColor, LedPreset

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
