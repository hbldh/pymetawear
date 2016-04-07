v0.2.3 (2016-04-07)
===================
- Changed from using ``gattlib`` on its own to using
  ``pybluez`` with ``gattlib``
- Travis CI and Coveralls
- Travis CI deploys documetnation to gh-pages.
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
