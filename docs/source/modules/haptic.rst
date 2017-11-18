.. _modules_haptic:

Haptic module
=============

The PyMetaWear implementation of the ``libmetawear``
haptic module.

It is initialized at the creation of the :py:class:`~MetaWearClient`
client and can then be accessed in the ``haptic``
attribute of the client.

Example usage:

.. code-block:: python

    from pymetawear.client import MetaWearClient

    c = MetaWearClient('DD:3A:7D:4D:56:F0')

    # Activate the Haptic motor.
    c.haptic.start_motor(100, 500)

    # Activate the Haptic buzzer.
    c.haptic.start_buzzer(500)

API
---

.. automodule:: pymetawear.modules.haptic
   :members:
