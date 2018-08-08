.. _modules_temperature:

Temperature module
==================

The PyMetaWear implementation of the ``libmetawear``
temperature module.

It is initialized at the creation of the :py:class:`~MetaWearClient`
client and can then be accessed in the ``temperature``
attribute of the client.

Example usage:

.. code-block:: python

    from pymetawear.client import MetaWearClient

    c = MetaWearClient('DD:3A:7D:4D:56:F0')

    def temperature_callback(data):
        """Handle a temperature notification data."""
        epoch = data[0]
        temp = data[1]
        print("[{0}] Temperature {1} C".format(epoch, temp))

    # Enable notifications and register a callback for them.
    c.temperature.notifications(temperature_callback)
    # Trigger temperature notification.
    c.temperature.read_temperature()

API
---

.. automodule:: pymetawear.modules.temperature
   :members:
