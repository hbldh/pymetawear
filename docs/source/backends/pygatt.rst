.. _backend_pygatt:

Backend: :mod:`pygatt`
======================

PyMetaWear can use ``pygatt`` as BLE communication backend.

Code can be found on `Github <https://github.com/peplin/pygatt>`_.

.. automodule:: pymetawear.backends.pygatt
   :members:


PyMetaWearGATTToolBackend
-------------------------

Some parts of the ``gatttool`` connection client did not work properly with the MetaWear boards.
Right now, these bugs are circumvented by overriding the offending methods.

.. automodule:: pymetawear.backends.pygatt.gatttool
   :members:
