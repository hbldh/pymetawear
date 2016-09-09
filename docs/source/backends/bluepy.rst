.. _backend_bleupy:

Backend: :mod:`bluepy`
======================

PyMetaWear can use ``bluepy`` as BLE communication backend. It is also uses
BlueZ to perform the actual communication, but it bundles the components it
needs to do it instead of utilizing the system installation.

   Right now the PyMetaWear implementation using ``bluepy`` lacks
   a proper handling of notifications!

The code can be found on `Github <https://github.com/IanHarvey/bluepy/>`_.

It can be installed separately as such:

.. code-block:: bash

   $ pip install bluepy

.. automodule:: pymetawear.backends.bluepy
   :members:
