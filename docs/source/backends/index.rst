.. _backend_index:

The :py:class:`~MetaWearClient` in itself mostly contains convenience
methods handling MetaWear specific tasks such as setting data rates
for accelerometers and subscribing to switch status. The actual Bluetooth
Low Energy communication is done in this module.

Currently, PyMetaWear implements three different backends:

.. toctree::
   :maxdepth: 1

   pygatt
   pybluez
   bluepy

