.. _modules_sensor_fusion:

Sensor Fusion module
====================

The PyMetaWear implementation of the ``libmetawear``
sensor fusion module.

It is initialized at the creation of the :py:class:`~MetaWearClient`
client and can then be accessed in the ``sensorfusion``
attribute of the client.

Example usage:

.. code-block:: python

    from pymetawear.client import MetaWearClient
    from mbientlab.metawear.cbindings import SensorFusionData, SensorFusionMode

    c = MetaWearClient('DD:3A:7D:4D:56:F0')

    c.sensorfusion.set_mode(SensorFusionMode.NDOF)
    c.sensorfusion.set_sample_delay(SensorFusionData.QUATERION, 20)

    def sensor_fusion_callback(data):
        """Handle sensor fusion notification data."""
        epoch = data[0]
        sf_data = data[1]
        print("[{0}] {1}".format(epoch, sf_data))

    c.sensorfusion.notifications(
        corrected_acc_callback=sensor_fusion_callback,
        quaternion_callback=sensor_fusion_callback,
        corrected_gyro_callback=sensor_fusion_callback)



API
---

.. automodule:: pymetawear.modules.sensorfusion
   :members:
