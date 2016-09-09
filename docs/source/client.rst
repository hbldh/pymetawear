.. _client:

MetaWear Client
===============

The MetaWear client provided by this package. It can be used as such:

.. code-block:: python

    from pymetawear.client import MetaWearClient
    backend = 'pygatt'  # Or 'pybluez' or 'bluepy'
    c = MetaWearClient('DD:3A:7D:4D:56:F0', backend)

The client can now be used for e.g. subscribing to data signals or logging data.

API
---

.. automodule:: pymetawear.client
    :members:
      MetaWearClient
