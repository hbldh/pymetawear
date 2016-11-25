#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:mod:`test_mwclient`
==================

Created by hbldh <henrik.blidh@nedomkull.com>
Created on 2016-04-06

"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

try:
    from unittest import mock
except:
    import mock

import pytest

import pymetawear.client
pymetawear.client.PyGattBackend = mock.Mock(pymetawear.client.PyGattBackend)


def test_dummy():
    pymetawear.client.PyGattBackend = mock.Mock(pymetawear.client.PyGattBackend)

    c = pymetawear.client.MetaWearClient('XX:XX:XX:XX:XX:XX', backend='pygatt')
    assert c.backend


