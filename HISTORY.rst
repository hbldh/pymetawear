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
