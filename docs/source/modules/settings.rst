.. _modules_settings:

Settings module
===============

Battery submodule
-----------------

The PyMetaWear implementation of the ``libmetawear``
switch module.

It is initialized at the creation of the :py:class:`~MetaWearClient`
client and can then be accessed in the ``battery``
attribute of the client.

Example usage:

.. code-block:: python

    from pymetawear.client import MetaWearClient

    c = MetaWearClient('DD:3A:7D:4D:56:F0')

    def battery_callback(data):
    """Handle a battery status tuple."""
        print("Voltage: {0}, Charge: {1}".format(
            data[0], data[1]))
    # Enable notifications and register a callback for them.
    mwclient.battery.notifications(battery_callback)
    # Trigger battery status notification.
    mwclient.battery.read_battery_state()




API
~~~

.. automodule:: pymetawear.modules.battery
   :members:
