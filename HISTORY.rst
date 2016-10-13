v0.5.2 (2016-10-13)
===================
- Temperature Module
- Using Pygatt 3.0.0 (including PR from PyMetaWear contributors)
- Builds on Windows

v0.5.1 (2016-09-15)
===================
- Corrections to make it distributable via PyPI.

v0.5.0 (2016-09-15)
===================
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
===================
- Updated MetaWear-CppAPI submodule version.
- Removed temporary build workaround.

v0.4.3 (2016-04-27)
===================
- Critical fix for switch notifications.
- Updated MetaWear-CppAPI submodule version.
- Now using the new ``setup_metawear`` method.
- Restructured the ``IS_64_BIT`` usage which is still needed.

v0.4.2 (2016-04-27)
===================
- Critical fix for timeout in pybluez/gattlib backend.
- Added Gyroscope module.
- Added soft reset method to client.
- Updated examples.
- Updated documentation.

v0.4.1 (2016-04-20)
===================
- Cleanup of new modules sensor data parsing.
- Bug fix related to accelerometer module.
- Timeout parameter for client and backends.

v0.4.0 (2016-04-17)
===================
- Major refactorisation into new module layout.
- New examples using the new module handling.
- Accelerometer convenience methods shows strange lag still.

v0.3.1 (2016-04-10)
===================
- Critical fix for data signal subscription method.
- ``Setup.py`` handling of building made better,
- Documentation improved.

v0.3.0 (2016-04-09)
===================
- Major refactoring: all BLE comm code practically moved to backends.
- Backend ``pybluez`` with ``gattlib`` now works well.
- Travis CI problems with Python 2.7 encoding led to
  that we are now building on 2.7.11

v0.2.3 (2016-04-07)
===================
- Changed from using ``gattlib`` on its own to using
  ``pybluez`` with ``gattlib``
- Travis CI and Coveralls
- Travis CI deploys documentation to gh-pages.
- Some documentation written.

v0.2.2 (2016-04-06)
===================
- Convenience method for switch.
- Sphinx documentation added.
- Docstring updates.

v0.2.1 (2016-04-04)
===================
- Refactoring in moving functionality back to client from backends.
- Enable BlueZ 4.X use with ``pygatt``.
- Disconnect methods added.
- Example with switch button notification.

v0.2.0 (2016-04-02)
===================
- Two backends: ``pygatt`` and ``gattlib``
- ``pygatt`` backend can be fully initialize, i.e. handles notifications.
- ``gattlib`` backend **cannot** fully initialize, i.e. does **not** handles notifications.

v0.1.1 (2016-03-30)
===================
- Fix to support Python 3

v0.1.0 (2016-03-30)
===================
- Initial release
- Working communication, tested with very few API options.
