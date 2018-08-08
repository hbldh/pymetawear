.. _modules_switch:

Switch module
=============

The PyMetaWear implementation of the ``libmetawear``
switch module.

It is initialized at the creation of the :py:class:`~MetaWearClient`
client and can then be accessed in the ``switch``
attribute of the client.

Example usage:

.. code-block:: python

    from pymetawear.client import MetaWearClient

    c = MetaWearClient('DD:3A:7D:4D:56:F0')

    def switch_callback(data):
        """Handle a switch status integer (1 for pressed, 0 for released.)."""
        if data == 1:
            print("Switch pressed!")
        elif data == 0:
            print("Switch released!")

    # Enable notifications and register a callback for them.
    c.switch.notifications(switch_callback)

API
---

.. automodule:: pymetawear.modules.switch
   :members:
