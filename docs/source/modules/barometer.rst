.. _modules_barometer:

Barometer module
================

The PyMetaWear implementation of the ``libmetawear``
barometer module.

It is initialized at the creation of the :py:class:`~MetaWearClient`
client and can then be accessed in the ``barometer``
attribute of the client.

Example usage:

.. code-block:: python

    from pymetawear.client import MetaWearClient

    c = MetaWearClient('DD:3A:7D:4D:56:F0')

    # Set a large oversampling value.
    c.barometer.set_settings(oversampling='ultra_high')

    def barometer_callback(data):
        """Handle a (epoch, altitude) barometer tuple."""
        print("[{0}]: Altitude: {1} m".format(*data))

    # Enable notifications and register a callback for them.
    c.barometer.notifications(barometer_callback)

API
---

.. automodule:: pymetawear.modules.barometer
   :members:
