PyMetawear
==========

.. image:: https://readthedocs.org/projects/pymetawear/badge/?version=latest
    :target: http://pymetawear.readthedocs.org/en/latest/?badge=latest
    :alt: Documentation Status

Python package for connecting to and using `MbientLab's MetaWear <https://mbientlab.com/>`_ boards.

PyMetawear is a slim wrapper around the `MetaWear C++ API <https://github.com/mbientlab/Metawear-CppAPI>`_,
which is included as a Git submodule. It has support for using either
`pygattlib <https://bitbucket.org/OscarAcena/pygattlib>`_ or
`pygatt <https://github.com/peplin/pygatt>`_ for
Bluetooth Low Energy communication.

    - **PyMetaWear currently only works with the** ``pygatt`` **backend!**
    - PyMetaWear is currently a Linux only package! 
    - PyMetaWear is only tested with Ubuntu 15.10 as of yet!
    - PyMetaWear is only tested with Python 2.7.10 as of yet!

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

Available on [Github pages](https://hbldh.github.io/pymetawear/) of this repository.

Basic Usage
-----------

Currently, this MetaWear client is a pretty thin object, only handling the Bluetooth connection and
actual communication and mostly being called indirectly from the ``libmetawear`` C++ library:

.. code-block:: python
    
    from ctypes import byref
    from pymetawear.backends import *
    from pymetawear.mbientlab.metawear.peripheral import Led

    # Discovering nearby MetaWear boards.
    # N.B. Might require sudo access! Check `discover_devices` docstring for solution.
    metawear_devices = discover_devices(timeout=3)
    if len(metawear_devices) < 1:
        raise ValueError("No MetaWear devices could be detected.")
    else:
        address = metawear_devices[0][0]

    c = MetaWearClientPyGatt(address)

    # Blinking 10 times with green LED.

    pattern = Led.Pattern(repeat_count=10)
    libmetawear.mbl_mw_led_load_preset_pattern(byref(pattern), Led.PRESET_BLINK)
    libmetawear.mbl_mw_led_write_pattern(c.board, byref(pattern), Led.COLOR_GREEN)
    libmetawear.mbl_mw_led_play(c.board)

See the examples folder for more examples on how to use the ``libmetawear`` library with this client.
