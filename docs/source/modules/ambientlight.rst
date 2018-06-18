.. _modules_accelerometer:

Ambient light module
====================

The PyMetaWear implementation of the ``libmetawear``
ambient light module.

It is initialized at the creation of the :py:class:`~MetaWearClient`
client and can then be accessed in the ``ambient_light``
attribute of the client.

Data streaming example
----------------------

If you need a real time stream of sensor data, use the :py:method:`notifications` method on the :py:mod:`ambient_light` module:

.. code-block:: python

    from pymetawear.client import MetaWearClient

    c = MetaWearClient('DD:3A:7D:4D:56:F0')

    print("Write ambient light settings...")
    c.ambient_light.set_settings(gain=4, integration_time=200, measurement_rate=200)

    def ambient_light_callback(data):
        """Handle a (epoch, data) ambient light data tuple."""
        print("Epoch time: [{0}] Data: {1}".format(data[0], data[1]))

    # Enable notifications and register a callback for them.
    c.ambient_light.notifications(ambient_light_callback)
    

API
---

.. automodule:: pymetawear.modules.ambientlight
   :members:
