#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""

.. moduleauthor:: hbldh <henrik.blidh@nedomkull.com>
Created on 2016-04-02

"""

from __future__ import division
from __future__ import print_function
#from __future__ import unicode_literals
from __future__ import absolute_import

import uuid

from ctypes import create_string_buffer
from pygatt import BLEAddressType
from pygatt.backends.gatttool import gatttool

from pymetawear.exceptions import PyMetaWearException, PyMetaWearConnectionTimeout
from pymetawear.utils import range_
from pymetawear.backends import BLECommunicationBackend

__all__ = ["PyGattBackend"]


class PyGattBackend(BLECommunicationBackend):
    """
    Backend using `pygatt <https://github.com/peplin/pygatt>`_
    for BLE communication.
    """

    def __init__(self, address, interface=None, async=True, timeout=None, debug=False):

        self._backend = None
        super(PyGattBackend, self).__init__(
            address, interface, async,
            gatttool.DEFAULT_CONNECT_TIMEOUT_S if timeout is None else timeout,
            debug)

    @property
    def requester(self):
        """Property handling the backend's device instance and its connection.

        :return: A connected ``pygatt`` BLE device instance.
        :rtype: :class:`pygatt.device.BLEDevice`

        """
        if self._requester is None:
            if self._debug:
                print("Creating new GATTToolBackend and starting GATTtool process...")
            self._backend = gatttool.GATTToolBackend(hci_device=self._interface)
            self._backend.start(reset_on_start=False)
            if self._debug:
                print("Connecting GATTTool...")
            self._requester = self._backend.connect(
                self._address, timeout=self._timeout, address_type=BLEAddressType.random)

            if not self.requester._connected:
                raise PyMetaWearConnectionTimeout(
                    "Could not establish a connection to {0}.".format(
                        self._address))

        return self._requester

    def disconnect(self):
        """Disconnect via the GATTTool process and terminate the
        interactive prompt.

        We can use the `stop` method since only one client can be
        connected to one GATTTool backend.

        """
        if self._backend is not None and self._backend:
            self._backend.stop()
        self._backend = None
        self._requester = None

    def _subscribe(self, characteristic_uuid, callback):
        return self.requester.subscribe(str(characteristic_uuid), callback)

    def read_gatt_char_by_uuid(self, characteristic_uuid):
        """Read the desired data from the MetaWear board using pygatt backend.

        :param pymetawear.mbientlab.metawear.core.GattCharacteristic
            characteristic: :class:`ctypes.POINTER` to a GattCharacteristic.
        :return: The read data.
        :rtype: str

        """
        return self.requester.char_read(str(characteristic_uuid))

    def write_gatt_char_by_uuid(self, characteristic_uuid, data_to_send):
        """Write the desired data to the MetaWear board using pygatt backend.

        :param uuid.UUID characteristic_uuid: The UUID to the characteristic
            to write to.
        :param str data_to_send: Data to send.

        """
        self.requester.char_write(str(characteristic_uuid), data_to_send)

    def get_handle(self, uuid, notify_handle=False):
        """Get handle from characteristic UUID.

        :param uuid.UUID uuid: The UUID to find handle to.
        :param bool notify_handle:
        :return: Integer handle.
        :rtype: int

        """
        return self.requester.get_handle(uuid) + int(notify_handle)

    @staticmethod
    def mbl_mw_command_to_input(command, length):
        return bytearray([command[i] for i in range_(length)])

    @staticmethod
    def read_response_to_str(response):
        return create_string_buffer(bytes(response), len(response))

    @staticmethod
    def notify_response_to_str(response):
        return create_string_buffer(bytes(response), len(response))
