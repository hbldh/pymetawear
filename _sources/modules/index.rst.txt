.. _modules_index:

MetaWear modules
================

.. toctree::
   :maxdepth: 1

   base
   accelerometer
   gyroscope
   magnetometer
   barometer
   led
   ambientlight
   settings
   haptic
   switch
   temperature
   sensor_fusion


There are two major modalities for obtaining data from sensors: subscribing to data from it or logging the data 
to the MetaWear board for subsequent download.

Streaming data
--------------

Streaming the data is a method of data extraction that is preferable if you have a need of the data in real-time,
e.g. for IMU navigation. It sends a epoch time tagged dictionary to a callback function specified by you, to process
as you see fit.

Streaming is also the only option that allows for access to high frequency (>400 Hz) data for accelerometer and gyroscope.

Modules supporting continuous data streaming:

- :py:mod:`accelerometer`
- :py:mod:`gyroscope`
- :py:mod:`magnetometer`
- :py:mod:`barometer`
- :py:mod:`switch`
- :py:mod:`ambientlight`
- :py:mod:`sensor_fusion`

Modules supporting notification protocol, but notifications are received by manually triggering them:

- :py:mod:`temperature`
- :py:mod:`settings` (battery)

Logging data
------------

If you are not dependent on having data delivered continuously but rather just need it saved for analysis later on, then
logging it to the board is a better choice. It reduces the potential for BLE disconnections during data recording, making
it a more stable means of ensuring that data is actually collected.

Modules supporting logging data (at least with PyMetaWear implementation):

- :py:mod:`accelerometer`
- :py:mod:`gyroscope`
- :py:mod:`magnetometer`
- :py:mod:`sensor_fusion`
