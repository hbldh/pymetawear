.. PyMetaWear documentation master file, created by
   sphinx-quickstart on Wed Apr  6 15:41:48 2016.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

PyMetaWear documentation
========================

.. image:: https://travis-ci.org/hbldh/pymetawear.svg?branch=master
    :target: https://travis-ci.org/hbldh/pymetawear

.. image:: https://coveralls.io/repos/github/hbldh/pymetawear/badge.svg?branch=master
    :target: https://coveralls.io/github/hbldh/pymetawear?branch=master

Python package for connecting to and using
`MbientLab's MetaWear <https://mbientlab.com/>`_ boards.

PyMetaWear was previously a wrapper around the
`MetaWear C++ API <https://github.com/mbientlab/Metawear-CppAPI>`_,
providing a more Pythonic interface. In version 0.9.0 it instead becomes
a wrapper around `MetaWear's official Python SDK <https://github.com/mbientlab/MetaWear-SDK-Python>`_,
doing the very same thing. The official SDK handles the actual board
connections and communication while PyMetaWear aims to remove the low level
feeling of interacting with the MetaWear board.

PyMetaWear can, from version 0.11.0, be used from both Windows and Linux. This is due to
`metawear package <https://github.com/mbientlab/MetaWear-SDK-Python>`_ depending on a new BLE library called
`PyWarble <https://github.com/mbientlab/PyWarble>`_. See installation instructions for more details about
how to make it build on Windows.


Contents
--------

.. toctree::
   :maxdepth: 2

   discover
   client
   exceptions
   modules/index
   history
   authors

Installation
------------

.. code-block:: bash

    $ pip install pymetawear

Since version 0.11.0, the installation requirements for ``pymetawear`` has changed some:

Linux
+++++

From ``PyWarble``'s README:

> You will need to have BlueZ, Boost headers, and GNU Make installed along with a C++ compiler that support C++14.

On Ubuntu this translates to installing the following:

.. code-block:: bash

    $ sudo apt-get install build-essential cmake bluez libbluetooth-dev

Windows
+++++++

On Windows, you need to install Visual Studio 2017 to be able to build and install the ``pymetawear`` package.
Furthermore, at least the Fall Creators Update SDK is needed.

Make sure that your ``MSBuild.exe`` file is available in your PATH before running the install command.


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

