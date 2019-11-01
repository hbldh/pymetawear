.. PyMetaWear documentation master file, created by
   sphinx-quickstart on Wed Apr  6 15:41:48 2016.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

PyMetaWear documentation
========================

.. image:: https://dev.azure.com/hbldh/github/_apis/build/status/hbldh.pymetawear?branchName=master
    :target: https://dev.azure.com/hbldh/github/_build/latest?definitionId=1?branchName=master

.. image:: https://coveralls.io/repos/github/hbldh/pymetawear/badge.svg?branch=master
    :target: https://coveralls.io/github/hbldh/pymetawear?branch=master

**PyMetaWear is a community developed Python SDK started by**
`Henrik Blidh <https://github.com/hbldh>`_ **. MbientLab does not provide support for this SDK.**

Python package for connecting to and using
`MbientLab's MetaWear <https://mbientlab.com/>`_ boards.

PyMetaWear was previously a wrapper around the
`MetaWear C++ API <https://github.com/mbientlab/Metawear-CppAPI>`_,
providing a more Pythonic interface. In version 0.9.0 it instead becomes
a wrapper around `MetaWear's official Python SDK <https://github.com/mbientlab/MetaWear-SDK-Python>`_,
doing the very same thing. The official SDK handles the actual board
connections and communication while PyMetaWear aims to remove the low level
feeling of interacting with the MetaWear board.

PyMetaWear can, from version 0.11.0, be used from both Windows and Linux. This is thanks to that the
``metawear`` `package <https://github.com/mbientlab/MetaWear-SDK-Python>`_ package is now depending on a
new BLE library called `PyWarble <https://github.com/mbientlab/PyWarble>`_ instead of ``gattlib``.
See installation instructions for more details about how to make it build on Windows.


Contents
--------

.. toctree::
   :maxdepth: 2

   installation
   discover
   client
   exceptions
   modules/index
   history
   authors


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

