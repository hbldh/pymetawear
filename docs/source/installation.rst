Installation
============

.. code-block:: bash

    $ pip install pymetawear

Since version 0.11.0, the installation requirements for ``pymetawear`` has changed some.

Linux
-----

From ``PyWarble``'s README: *You will need to have BlueZ, Boost headers, and GNU Make installed along with a C++ compiler that support C++14.*

On Ubuntu this translates to installing the following:

.. code-block:: bash

    $ sudo apt-get install build-essential cmake bluez libbluetooth-dev libboost-dev

Windows
-------

On Windows, you need to install Visual Studio 2017 to be able to build and install the ``pymetawear`` package.
Furthermore, at least the Fall Creators Update SDK is needed.

Make sure that your ``MSBuild.exe`` file is available in your PATH before running the install command.

See `PyWarble's README <https://github.com/mbientlab/PyWarble>`_ for more details.