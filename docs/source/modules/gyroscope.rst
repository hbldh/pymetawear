.. _modules_gyroscope:

Gyroscope module
====================

The PyMetaWear implementation of the ``libmetawear``
gyroscope module.

It is initialized at the creation of the :py:class:`~MetaWearClient`
client and can then be accessed in the ``gyroscope``
attribute of the client.

The only MetaWear gyroscope available is the BMI160 sensor.

Data streaming example
----------------------

If you need a real time stream of sensor data, use the :py:func:`notifications` method on the :py:mod:`gyroscope` module:

.. code-block:: python

    from pymetawear.client import MetaWearClient

    c = MetaWearClient('DD:3A:7D:4D:56:F0')

    # Set data rate to 200 Hz and measuring range to +/- 1000 DPS
    c.gyroscope.set_settings(data_rate=200.0, data_range=1000.0)

    def gyro_callback(data):
        """Handle a (epoch, (x,y,z)) gyroscope tuple."""
        print("Epoch time: [{0}] - X: {1}, Y: {2}, Z: {3}".format(data[0], *data[1]))

    # Enable notifications and register a callback for them.
    c.gyroscope.notifications(gyro_callback)

Logging Example
---------------

If you want to log data to the MetaWear board and retrieve it after some time, then use the
:py:func:`start_logging`, :py:func:`stop_logging` and :py:func:`download_log` methods:

.. code-block:: python

    import os
    import json
    import time

    from pymetawear.client import MetaWearClient
    from pymetawear.exceptions import PyMetaWearException, PyMetaWearDownloadTimeout

    c = MetaWearClient('DD:3A:7D:4D:56:F0')

    # Set data rate to 200 Hz and measuring range to +/- 1000 DPS
    c.gyroscope.set_settings(data_rate=200.0, data_range=1000.0)

    # Log data for 10 seconds.
    c.gyroscope.start_logging()
    print("Logging gyroscope data...")

    time.sleep(10.0)

    c.gyroscope.stop_logging()
    print("Finished logging.")

    # Download the stored data from the MetaWear board.
    print("Downloading data...")
    download_done = False
    n = 0
    data = None
    while (not download_done) and n < 3:
        try:
            data = c.gyroscope.download_log()
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

.. automodule:: pymetawear.modules.gyroscope
   :members:
