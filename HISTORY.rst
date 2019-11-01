=======
History
=======

v0.12.0 (2019-11-01)
-----------------------

- Using ``metawear`` version ``0.7.0``


v0.11.1 (2019-10-08)
-----------------------

- Fixes #57
- Merges #54.
- Added first draft of Azure Pipelines CI building.

v0.11.0 (2018-08-08)
--------------------
- Using ``metawear`` version ``0.5.0``
- Possible to use on Windows thanks to new dependency in ``metawear`` >= ``0.4.0``

v0.10.1 (2018-08-08)
--------------------
- Fix for Haptic module, thanks to ``bgromov`` (#51)

v0.10.0 (2018-06-18)
--------------------
- Added support for data logging, thanks to ``dmatthes1982`` (#32, #46, #48, #49)
- Locked ``metawear`` version to ``0.3.1``
- Documentation for data logging
- Fixes for code examples and documentation examples.

v0.9.1 (2018-04-02)
-------------------
- Fix for documentation and README

v0.9.0 (2018-04-02)
-------------------
- Ownership returned to original owner
- Using MetaWear-Python-SDK instead of Cpp directly

v0.8.0 (2017-07-04)
-------------------
- Using MetaWear-CppAPI version 0.8.0
- New ownership

v0.7.1 (2017-02-04)
-------------------
- Using MetaWear-CppAPI version 0.7.10
- Sensor fusion module contributed from user ``m-georgi`` (#26).
- Fix to magnetometer power preset setting due to
  change in MetaWear-CppAPI (#25).

v0.7.0 (2017-01-13)
-------------------
- Using MetaWear-CppAPI version 0.7.4
- Removed bluepy backend due to it not being fully functional.
- Refactored connection behaviour. Optional autoconnect via keyword.
- Unit test work started with Mock backend.
- Flake8 adaptations.
- Fix for logging bug (#22)
- New examples: Two client setup and complimentary filter sensor fusion (#23).

v0.6.0 (2016-10-31)
-------------------
- Using MetaWear-CppAPI version 0.6.0
- Replaced print-logging with proper logging module usage.
- Removed 64-bit special handling that was no longer needed.

v0.5.2 (2016-10-13)
-------------------
- Temperature Module
- Using Pygatt 3.0.0 (including PR from PyMetaWear contributors)
- Builds on Windows

v0.5.1 (2016-09-15)
-------------------
- Corrections to make it distributable via PyPI.

v0.5.0 (2016-09-15)
-------------------
- Using MetaWear-CppAPI version 0.5.22
- Changed building procedure to handle ARM processors
- Updated requirements to make pygatt default, all others extras
- Bluepy backend implemented and partially working
- BL interface selection for all backends
- Magnetometer module
- Barometer module
- Ambient Light module
- Modifying notification wrappers to accommodate Epoch value in the data.
- High speed sampling for accelerometer and gyroscope

v0.4.4 (2016-04-28)
-------------------
- Updated MetaWear-CppAPI submodule version.
- Removed temporary build workaround.

v0.4.3 (2016-04-27)
-------------------
- Critical fix for switch notifications.
- Updated MetaWear-CppAPI submodule version.
- Now using the new ``setup_metawear`` method.
- Restructured the ``IS_64_BIT`` usage which is still needed.

v0.4.2 (2016-04-27)
-------------------
- Critical fix for timeout in pybluez/gattlib backend.
- Added Gyroscope module.
- Added soft reset method to client.
- Updated examples.
- Updated documentation.

v0.4.1 (2016-04-20)
-------------------
- Cleanup of new modules sensor data parsing.
- Bug fix related to accelerometer module.
- Timeout parameter for client and backends.

v0.4.0 (2016-04-17)
-------------------
- Major refactorisation into new module layout.
- New examples using the new module handling.
- Accelerometer convenience methods shows strange lag still.

v0.3.1 (2016-04-10)
-------------------
- Critical fix for data signal subscription method.
- ``Setup.py`` handling of building made better,
- Documentation improved.

v0.3.0 (2016-04-09)
-------------------
- Major refactoring: all BLE comm code practically moved to backends.
- Backend ``pybluez`` with ``gattlib`` now works well.
- Travis CI problems with Python 2.7 encoding led to
  that we are now building on 2.7.11

v0.2.3 (2016-04-07)
-------------------
- Changed from using ``gattlib`` on its own to using
  ``pybluez`` with ``gattlib``
- Travis CI and Coveralls
- Travis CI deploys documentation to gh-pages.
- Some documentation written.

v0.2.2 (2016-04-06)
-------------------
- Convenience method for switch.
- Sphinx documentation added.
- Docstring updates.

v0.2.1 (2016-04-04)
-------------------
- Refactoring in moving functionality back to client from backends.
- Enable BlueZ 4.X use with ``pygatt``.
- Disconnect methods added.
- Example with switch button notification.

v0.2.0 (2016-04-02)
-------------------
- Two backends: ``pygatt`` and ``gattlib``
- ``pygatt`` backend can be fully initialize, i.e. handles notifications.
- ``gattlib`` backend **cannot** fully initialize, i.e. does **not** handles notifications.

v0.1.1 (2016-03-30)
-------------------
- Fix to support Python 3

v0.1.0 (2016-03-30)
-------------------
- Initial release
- Working communication, tested with very few API options.
