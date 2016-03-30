PyMetawear
==========

Python package for connecting to and using `MbientLab's MetaWear <https://mbientlab.com/>`_ boards.

PyMetawear is a slim wrapper around the `MetaWear C++ API <https://github.com/mbientlab/Metawear-CppAPI>`_,
which is included as a Git submodule. It uses the `pybluez <https://github.com/karulis/pybluez>`_ package,
which in its turn uses `pygattlib <https://bitbucket.org/OscarAcena/pygattlib>`_ for
Bluetooth Low Energy communication.

    - PyMetaWear is currently a Linux only package! 
    - PyMetaWear is only tested with Ubuntu 14.04 as of yet!
    - PyMetaWear has only been tested with Python 2.7.10!

Installation
------------

First, make sure all dependencies are installed:

.. code-block:: bash

    $ sudo apt-get install python-dev bluetooth libbluetooth-dev

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

Usage
-----

Currently, the `MetaWearClient` is a pretty thin object, only handling the Bluetooth connection and
actual communication and mostly being called indirectly from the ``libmetawear`` C++ library:

.. code-block:: python
    
    from ctypes import byref
    from pymetawear.client import discover_devices, MetaWearClient, libmetawear
    from pymetawear.mbientlab.metawear.peripheral import Led

    # Discovering nearby MetaWear boards.
    # N.B. Might require sudo access! Check `discover_devices` docstring for solution.
    metawear_devices = discover_devices(timeout=3)
    if len(metawear_devices) < 1:
        raise ValueError("No MetaWear devices could be detected.")
    else:
        address = metawear_devices[0][0]

    c = MetaWearClient(address)

    # Blinking 10 times with green LED.

    pattern = Led.Pattern(repeat_count=10)
    libmetawear.mbl_mw_led_load_preset_pattern(byref(pattern), Led.PRESET_BLINK)
    libmetawear.mbl_mw_led_write_pattern(c.board, byref(pattern), Led.COLOR_GREEN)
    libmetawear.mbl_mw_led_play(c.board)

    # Reading battery state.
    battery_state = libmetawear.mbl_mw_settings_read_battery_state(c.board)

