.. _modules_accelerometer:

Accelerometer module
====================

The PyMetaWear implementation of the ``libmetawear``
accelerometer module.

It is initialized at the creation of the :py:class:`~MetaWearClient`
client and can then be accessed in the ``accelerometer``
attribute of the client.

Example usage:

.. code-block:: python

    from pymetawear.client import MetaWearClient

    c = MetaWearClient('DD:3A:7D:4D:56:F0')

    # Set data rate to 200 Hz and measureing range to +/- 8g
    c.accelerometer.set_settings(data_rate=200.0, data_range=8)

    def handle_acc_notification(data):
        """Handle a (x,y,z) accelerometer tuple."""
        print("X: {0}, Y: {1}, Z: {2}".format(*data))

    # Enable notifications and register a callback for them.
    c.accelerometer.notifications(handle_acc_notifications)

API
---

.. automodule:: pymetawear.modules.accelerometer
   :members:
