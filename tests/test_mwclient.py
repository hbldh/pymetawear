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

import pytest

import pymetawear.client
from .mock_backend import MockBackend
pymetawear.client.MetaWear = MockBackend

@pytest.mark.parametrize("mw_board", range(7))
@pytest.mark.skip(reason='Needs to be updated for 0.9.0 breaking changes')
def test_client_init(mw_board):
    MockBackend.boardType = mw_board
    c = pymetawear.client.MetaWearClient('XX:XX:XX:XX:XX:XX', debug=False)
    assert isinstance(c.mw, MockBackend)
    assert c.mw.boardType == mw_board
    assert c.mw.initialized
    assert c.mw.initialization_status == 0

    expected_cmds = [
        [0x01, 0x80], [0x02, 0x80], [0x03, 0x80], [0x04, 0x80],
        [0x05, 0x80], [0x06, 0x80], [0x07, 0x80], [0x08, 0x80],
        [0x09, 0x80], [0x0a, 0x80], [0x0b, 0x80], [0x0c, 0x80],
        [0x0d, 0x80], [0x0f, 0x80], [0x10, 0x80], [0x11, 0x80],
        [0x12, 0x80], [0x13, 0x80], [0x14, 0x80], [0x15, 0x80],
        [0x16, 0x80], [0x17, 0x80], [0x18, 0x80], [0x19, 0x80],
        [0xfe, 0x80], [0x0b, 0x84]
    ]
    assert c.mw.full_history == expected_cmds


@pytest.mark.parametrize("mw_board", range(7))
@pytest.mark.skip(reason='Needs to be updated for 0.9.0 breaking changes')
def test_client_init_delayed_connect(mw_board):
    MockBackend.boardType = mw_board
    c = pymetawear.client.MetaWearClient('XX:XX:XX:XX:XX:XX', connect=False, debug=False)
    assert isinstance(c.mw, MockBackend)
    assert not c.mw.initialized
    c.connect()
    assert c.mw.boardType == mw_board
    assert c.mw.initialized
    assert c.mw.initialization_status == 0

    expected_cmds = [
        [0x01, 0x80], [0x02, 0x80], [0x03, 0x80], [0x04, 0x80],
        [0x05, 0x80], [0x06, 0x80], [0x07, 0x80], [0x08, 0x80],
        [0x09, 0x80], [0x0a, 0x80], [0x0b, 0x80], [0x0c, 0x80],
        [0x0d, 0x80], [0x0f, 0x80], [0x10, 0x80], [0x11, 0x80],
        [0x12, 0x80], [0x13, 0x80], [0x14, 0x80], [0x15, 0x80],
        [0x16, 0x80], [0x17, 0x80], [0x18, 0x80], [0x19, 0x80],
        [0xfe, 0x80], [0x0b, 0x84]
    ]
    assert c.mw.full_history == expected_cmds


def test_client_creation():
    c = pymetawear.client.MetaWearClient('XX:XX:XX:XX:XX:XX', connect=False)
    assert c is not None
