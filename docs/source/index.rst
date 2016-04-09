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

Python package for connecting to and using `MbientLab's MetaWear <https://mbientlab.com/>`_ boards.

PyMetawear is a slim wrapper around the
`MetaWear C++ API <https://github.com/mbientlab/Metawear-CppAPI>`_,
which is included as a Git submodule. It has support for using either
`pybluez <https://github.com/karulis/pybluez>`_ and
`gattlib <https://bitbucket.org/OscarAcena/pygattlib>`_ or
`pygatt <https://github.com/peplin/pygatt>`_ for
Bluetooth Low Energy communication.

    - PyMetaWear is currently a Linux only package!
    - PyMetaWear is only tested with Ubuntu 14.04+ as of yet!
    - PyMetaWear is only tested with Python 2.7.10 as of yet!

Contents
--------

.. toctree::
   :maxdepth: 1

   discover
   client
   backends/index

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


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

