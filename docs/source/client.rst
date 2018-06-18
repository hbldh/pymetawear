.. _client:

MetaWear Client
===============

The MetaWear client provided by this package. It can be used as such:

.. code-block:: python

    from pymetawear.client import MetaWearClient
    c = MetaWearClient('DD:3A:7D:4D:56:F0')

The client can now be used for either reading the current module data or activate some functionality in it. 
There are two major modalities for obtaining data from sensors: subscribing to data from it or logging the data 
to the MetaWear board for subsequent download.

Streaming data
--------------

Streaming the data is a method of data extraction that is preferable if you have a need of the data in real-time,
e.g. for IMU navigation. It sends a epoch time tagged dictionary to a callback function specified by you, to process
as you see fit.

Streaming is also the only option that allows for access to high frequency (>400 Hz) data for accelerometer and gyroscope.

Logging data
------------

If you are not dependent on having data delivered continuously but rather just need it saved for analysis later on, then
logging it to the board is a better choice. It reduces the potential for BLE disconnections during data recording, making
it a more stable means of ensuring that data is actually collected.

API
---

.. automodule:: pymetawear.client
    :members:
      MetaWearClient
