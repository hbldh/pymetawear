PyMetawear
==========

.. image:: https://travis-ci.org/hbldh/pymetawear.svg?branch=master
    :target: https://travis-ci.org/hbldh/pymetawear
.. image:: https://coveralls.io/repos/github/hbldh/pymetawear/badge.svg?branch=master
    :target: https://coveralls.io/github/hbldh/pymetawear?branch=master

Python package for connecting to and using `MbientLab's MetaWear <https://mbientlab.com/>`_ boards.

PyMetawear is meant to be a thin wrapper around the
`MetaWear C++ API <https://github.com/mbientlab/Metawear-CppAPI>`_,
providing a more Pythonic interface. It has support for using either
`pybluez <https://github.com/karulis/pybluez>`_ and
`gattlib <https://bitbucket.org/OscarAcena/pygattlib>`_ or
`pygatt <https://github.com/peplin/pygatt>`_ for
Bluetooth Low Energy communication.

PyMetaWear can be run with Python 2.7 with both backends, but only with the `pygatt` backend for Python 3.

    - PyMetaWear is currently a Linux only package!
    - PyMetaWear is only tested with Ubuntu 14.04+ and Linux Mint 17 as of yet!

Installation
------------

First, make sure all dependencies are installed:

.. code-block:: bash

    $ sudo apt-get install cmake build-essential python-dev bluetooth libbluetooth-dev libboost-python-dev libboost-thread-dev

PyMetaWear can be installed from pip:

.. code-block:: bash

    $ pip install git+git://github.com/hbldh/pymetawear.git

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
    backend = 'pybluez'  # Or 'pygatt'
    c = MetaWearClient('DD:3A:7D:4D:56:F0', backend)

An example: blinking with the LED lights can be done like this with the
convenience methods:

.. code-block:: python

    # Will be written soon.

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
Accelerometer     Settings        All others
Haptic            LED
Switch
================= =============== =====================

