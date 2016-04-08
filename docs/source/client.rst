.. _client:

MetaWearClient
==============

The MetaWear client provided by this package.

.. code-block:: python

    from pymetawear import libmetawear
    from pymetawear.client import MetaWearClient
    from pymetawear.mbientlab.metawear.peripheral import Led

    # Discovering nearby MetaWear boards.
    # N.B. Might require sudo access! Check `discover_devices` docstring for solution.
    metawear_devices = discover_devices(timeout=3)
    if len(metawear_devices) < 1:
        raise ValueError("No MetaWear devices could be detected.")
    else:
        address = metawear_devices[0][0]

    backend = 'pygatt'  # Can also be set to 'pybluez'
    c = MetaWearClientPyGatt(address, backend)

API
---

.. automodule:: pymetawear.client
   :members:
       MetaWearClient
