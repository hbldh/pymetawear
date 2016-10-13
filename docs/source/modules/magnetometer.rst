.. _modules_magnetometer:

Magnetometer module
===================

The PyMetaWear implementation of the ``libmetawear``
magnetometer module.

It is initialized at the creation of the :py:class:`~MetaWearClient`
client and can then be accessed in the ``magnetometer``
attribute of the client.

Example usage:

.. code-block:: python

    from pymetawear.client import MetaWearClient

    c = MetaWearClient('DD:3A:7D:4D:56:F0')

    # Set Power preset to low power.
    c.magnetometer.set_settings(power_preset='low_power')

    def magnetometer_callback(data):
        """Handle a (epoch_time, (x,y,z)) magnetometer tuple."""
            epoch = data[0]
            xyz = data[1]
            print("[{0}] X: {1}, Y: {2}, Z: {3}".format(epoch, *xyz))

    # Enable notifications and register a callback for them.
    c.magnetometer.notifications(magnetometer_callback)

API
---

.. automodule:: pymetawear.modules.magnetometer
   :members:
