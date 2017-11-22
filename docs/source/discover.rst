Discovering MetaWear boards addresses
=====================================

If you do not know the address of your MetaWear board, it
can be found by performing a scan.

.. code-block:: python

    >>> from pymetawear.client import discover_devices
    >>> discover_devices()
    [(u'DD:3A:7D:4D:56:F0', u'MetaWear'), (u'FF:50:35:82:3B:5A', u'MetaWear')]

The :func:`~discover_devices` function uses the
``hcitool`` application, provided by the `BlueZ  <http://www.bluez.org/>`_
bluetooth application. See docstring below for more details about privileges
using ``hcitool`` from Python.

There is a convenience method named :func:`~select_device` as well, which
displays a list of devices to choose from.

API
---

.. automodule:: pymetawear.discover
    :members:
