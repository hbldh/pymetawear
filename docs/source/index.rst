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

**PyMetaWear is Linux-only**!


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

Due to a dependency on ``gattlib``, a Python BLE package that is
poorly maintained, MbientLab has `forked it <https://github.com/mbientlab/pygattlib>`
and ships a patched version with its Python SDK. This makes installation of
PyMetaWear require some additional work:

.. code-block:: bash

    $ pip install git+https://github.com/mbientlab/pygattlib.git@master#egg=gattlib
    $ pip install metawear
    $ pip install pymetawear

Please ensure that the `dependencies <https://bitbucket.org/OscarAcena/pygattlib/src/a858e8626a93cb9b4ad56f3fb980a6517a0702c6/DEPENDS?at=default&fileviewer=file-view-default>`_ for ``gattlib`` are fulfilled before installing.

Development
~~~~~~~~~~~

TBW.


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

