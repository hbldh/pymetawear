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



Contents
--------

.. toctree::
   :maxdepth: 2

   discover
   client
   exceptions
   backends/index
   modules/index

Installation
------------

.. code-block:: bash

    $ pip install git+git://github.com/hbldh/pymetawear.git

Currently, only the `pygatt <https://github.com/peplin/pygatt>`_ communication
backend is installed by default. The other backends can be installed as extras:

.. code-block:: bash

    $ pip install git+git://github.com/hbldh/pymetawear.git[pybluez]

or

.. code-block:: bash

    $ pip install git+git://github.com/hbldh/pymetawear.git[bluepy]

Requirements for ``pymetawear``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* ``build-essential``
* ``python-dev``

Additional requirements for ``pybluez``
~~~~~~~~~~~~~~~~~~~~~~~~~~~-~~~~~~~~~~~

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


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

