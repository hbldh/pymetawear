.. _backend_pygatt:

Backend: :mod:`pygatt`
======================

PyMetaWear uses ``pygatt`` as BLE communication backend by default.
This package uses `pexpect <https://pexpect.readthedocs.org/en/stable/>`_
to control the ``gatttool`` (part of BlueZ) command-line utility's
interactive terminal to communicate with Bluetooth LE devices.

Code can be found on `Github <https://github.com/peplin/pygatt>`_.

.. automodule:: pymetawear.backends.pygatt
   :members:


PyMetaWearGATTToolBackend
-------------------------

Some parts of the ``gatttool`` connection client did not work
properly with the MetaWear boards.
Right now, these bugs are circumvented by overriding the offending methods.

.. automodule:: pymetawear.backends.pygatt.gatttool
   :members:
