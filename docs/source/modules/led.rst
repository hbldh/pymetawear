.. _modules_led:

LED module
==========

The PyMetaWear implementation of the ``libmetawear``
LED module.

It is initialized at the creation of the :py:class:`~MetaWearClient`
client and can then be accessed in the ``led``
attribute of the client.

Example usage:

.. code-block:: python

    from pymetawear.client import MetaWearClient

    c = MetaWearClient('DD:3A:7D:4D:56:F0')

    # Blinking 10 times with green LED.
    pattern = c.led.load_preset_pattern('blink', repeat_count=10)
    c.led.write_pattern(pattern, 'g')
    c.led.play()

API
---

.. automodule:: pymetawear.modules.led
   :members:
