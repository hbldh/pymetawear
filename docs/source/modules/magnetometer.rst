.. _modules_magnetometer:

Magnetometer module
===================

The PyMetaWear implementation of the ``libmetawear``
magnetometer module.

It is initialized at the creation of the :py:class:`~MetaWearClient`
client and can then be accessed in the ``magnetometer``
attribute of the client.

Data streaming example
----------------------

If you need a real time stream of sensor data, use the
:py:method:`notifications` method on the :py:mod:`magnetometer` module:

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

Logging Example
---------------

If you want to log data to the MetaWear board and retrieve it after some time, then use the
:py:method:`start_logging`, :py:method:`stop_logging` and :py:method:`download_log` methods:

.. code-block:: python

    import os
    import json
    import time

    from pymetawear.client import MetaWearClient
    from pymetawear.exceptions import PyMetaWearException, PyMetaWearDownloadTimeout

    c = MetaWearClient('DD:3A:7D:4D:56:F0')

    # Set Power preset to low power.
    c.magnetometer.set_settings(power_preset='low_power')

    # Log data for 10 seconds.
    c.magnetometer.start_logging()
    print("Logging magnetometer data...")

    time.sleep(10.0)

    c.magnetometer.stop_logging()
    print("Finished logging.")

    # Download the stored data from the MetaWear board.
    print("Downloading data...")
    download_done = False
    n = 0
    data = None
    while (not download_done) and n < 3:
        try:
            data = c.magnetometer.download_log()
            download_done = True
        except PyMetaWearDownloadTimeout:
            print("Download of log interrupted. Trying to reconnect...")
            c.disconnect()
            c.connect()
            n += 1
    if data is None:
        raise PyMetaWearException("Download of logging data failed.")

    print("Disconnecting...")
    c.disconnect()

    # Save the logged data.
    class MetaWearDataEncoder(json.JSONEncoder):
        """JSON Encoder for converting ``mbientlab`` module's CartesianFloat
        class to data tuple ``(x,y,z)``."""
        def default(self, o):
            if isinstance(o, CartesianFloat):
                return o.x, o.y, o.z
            else:
                return super(MetaWearDataEncoder, self).default(o)

    data_file = os.path.join(os.getcwd(), "logged_data.json")
    print("Saving the data to file: {0}".format(data_file))
    with open("logged_data.json", "wt") as f:
        json.dump(data, f, indent=2)


API
---

.. automodule:: pymetawear.modules.magnetometer
   :members:
