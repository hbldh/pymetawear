PyMetaWear
==========

.. image:: https://travis-ci.org/hbldh/pymetawear.svg?branch=master
    :target: https://travis-ci.org/hbldh/pymetawear
.. image:: https://coveralls.io/repos/github/hbldh/pymetawear/badge.svg?branch=master
    :target: https://coveralls.io/github/hbldh/pymetawear?branch=master

Python package for connecting to and using
`MbientLab's MetaWear <https://mbientlab.com/>`_ boards.

PyMetawear is meant to be a thin wrapper around the
`MetaWear C++ API <https://github.com/mbientlab/Metawear-CppAPI>`_,
providing a more Pythonic interface. It has support for several different
Python packages for Bluetooth Low Energy communication:

- `pygatt <https://github.com/peplin/pygatt>`_
- `pybluez <https://github.com/karulis/pybluez>`_ with
  `gattlib <https://bitbucket.org/OscarAcena/pygattlib>`_
- `bluepy <https://github.com/IanHarvey/bluepy>`_ (not completely functional yet)

PyMetaWear can be run with Python 2 or 3 with both backends,
but only with the `pygatt` backend for Python 3.5. It builds and runs on Linux systems,
and can be built on Windows, given that Visual Studio Community 2015 has been installed first,
but there is no working backend for Windows BLE yet.

Installation
------------

.. code-block:: bash

    $ pip install pymetawear

Currently, only the `pygatt <https://github.com/peplin/pygatt>`_ communication
backend is installed by default. The other backends can be installed as extras:

.. code-block:: bash

    $ pip install pymetawear[pybluez]

or

.. code-block:: bash

    $ pip install pymetawear[bluepy]

Debian requirements for ``pymetawear``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* ``build-essential``
* ``python-dev``

Additional requirements for ``pybluez``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* ``libglib2.0-dev``
* ``bluetooth``
* ``libbluetooth-dev``
* ``libboost-python-dev``
* ``libboost-thread-dev``

Additional requirements for ``bluepy``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
* ``libglib2.0-dev``


Development
~~~~~~~~~~~

Clone this repository and run

.. code-block:: bash

    $ python setup.py build

to pull in the `MetaWear C++ API <https://github.com/mbientlab/Metawear-CppAPI>`_ submodule,
build it and copy the Python wrappers from it to the PyMetaWear folder. This can also be achieved by
running

.. code-block:: bash

    $ pip install -e .

in the cloned repository's root folder.

Documentation
-------------

Available in the `Github pages <https://hbldh.github.io/pymetawear/>`_
of this repository.

Basic Usage
-----------

The MetaWear client can be used in two ways: either as Pythonic
convenience class for handling a MetaWear board or as
a simple communication client governed by the ``libmetawear`` C++ library.

Creating a client, and thus also setting up a Bluetooth connection to the
MetaWear board, is equal for both the two usage profiles:

.. code-block:: python

    from pymetawear.client import MetaWearClient
    backend = 'pygatt'  # Or 'pybluez' or 'bluepy'
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
    from pymetawear.mbientlab.metawear.peripheral import Led

    pattern = Led.Pattern(repeat_count=10)
    libmetawear.mbl_mw_led_load_preset_pattern(byref(pattern), Led.PRESET_BLINK)
    libmetawear.mbl_mw_led_write_pattern(c.board, byref(pattern), Led.COLOR_GREEN)
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
Accelerometer     Settings        Temperature
Gyroscope                         Color Detector
Haptic                            Humidity
Switch                            GPIO
LED                               I2C
Barometer                         iBeacon
Magnetometer                      NeoPixel
                                  Proximity
================= =============== =====================
