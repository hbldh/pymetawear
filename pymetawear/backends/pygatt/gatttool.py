#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""

Created by hbldh <henrik.blidh@nedomkull.com>
Created on 2016-04-02

"""

from __future__ import division
from __future__ import print_function
#from __future__ import unicode_literals
from __future__ import absolute_import

import re
import subprocess

import pygatt
from pygatt.backends.gatttool.gatttool import DEFAULT_CONNECT_TIMEOUT_S, log, \
    NotConnectedError, NotificationTimeout, GATTToolBLEDevice, pexpect


class PyMetaWearGATTToolBackend(pygatt.backends.GATTToolBackend):
    """Minor modification of the GATTToolBackend to handle multiple byte output from notifications.

    Will be removed if pull request is accepted.

    """

    def __init__(self, *args, **kwargs):
        self._notification_regex = re.compile("=\s(0x[0-9a-fA-F]{4})\svalue:\s(.*)$")
        super(PyMetaWearGATTToolBackend, self).__init__(*args, **kwargs)

    def connect(self, address, timeout=DEFAULT_CONNECT_TIMEOUT_S,
                address_type='public'):
        # Try to discern if Bluez 4.X is used.
        try:
            p = subprocess.Popen(["dpkg", "--status", "bluez"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            output = subprocess.check_output(('grep', '^Version:'), stdin=p.stdout)
            p.wait()
            major, minor_plus = output.decode().split('Version:')[-1].strip().split('.', 1)
        except Exception as e:
            major = '5'

        log.info('Connecting with timeout=%s', timeout)
        self._con.sendline('sec-level low')
        self._address = address
        try:
            with self._connection_lock:
                cmd = 'connect %s %s' % (self._address, address_type)
                self._con.sendline(cmd)
                if int(major) < 5:
                    expect_str = self._address.encode().join([b'\[CON\]\[', b'\]\[LE\]'])
                    self._con.expect(expect_str, timeout)
                else:
                    self._con.expect(b'Connection successful.*\[LE\]>', timeout)
        except pexpect.TIMEOUT:
            message = ("Timed out connecting to %s after %s seconds."
                       % (self._address, timeout))
            log.error(message)
            raise NotConnectedError(message)

        self._connected_device = GATTToolBLEDevice(address, self)
        return self._connected_device

    def _handle_notification_string(self, msg):
        hex_handle, hex_values = self._notification_regex.search(msg.decode().strip()).groups()
        handle = int(hex_handle, 16)
        value = bytearray([int(x, 16) for x in hex_values.strip().split(' ')])
        if self._connected_device is not None:
            self._connected_device.receive_notification(handle, value)
