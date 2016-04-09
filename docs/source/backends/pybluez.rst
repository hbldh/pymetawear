.. _backend_gattlib:

Backend: :mod:`pybluez`
=======================

PyMetaWear can use ``pybluez`` as BLE communication backend. The package doing
the BLE communication is actually ``gattlib``, which can be found on
`Bitbucket <https://bitbucket.org/OscarAcena/pygattlib>`_. It is installed
as a subpackage to `pybluez <https://github.com/karulis/pybluez>`_, a
requirement to make documentation buildable on Travis CI.

It can be installed separately as such:

.. code-block:: bash

   $ pip install pybluez[ble]

.. automodule:: pymetawear.backends.pybluez
   :members:
