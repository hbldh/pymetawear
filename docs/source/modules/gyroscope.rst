.. _modules_accelerometer:

Gyroscope module
====================

The PyMetaWear implementation of the ``libmetawear``
gyroscope module.

It is initialized at the creation of the :py:class:`~MetaWearClient`
client and can then be accessed in the ``gyroscope``
attribute of the client.

The only MetaWear gyroscope available is the BMI160 sensor.

Example usage:

.. code-block:: python

    from pymetawear.client import MetaWearClient

    c = MetaWearClient('DD:3A:7D:4D:56:F0')

    # Set data rate to 200 Hz and measuring range to +/- 1000 DPS
    c.gyroscope.set_settings(data_rate=200.0, data_range=1000.0)

    def handle_notification(data):
        """Handle a (x,y,z) gyroscope tuple."""
        print("X: {0}, Y: {1}, Z: {2}".format(*data))

    # Enable notifications and register a callback for them.
    c.gyroscope.notifications(handle_notifications)

API
---

.. automodule:: pymetawear.modules.gyroscope
   :members:
