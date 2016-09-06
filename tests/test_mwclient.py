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
#from __future__ import unicode_literals
from __future__ import absolute_import

import pytest

from pymetawear.client import MetaWearClient
from pymetawear.backends import BLECommunicationBackend
from pymetawear.backends.pygatt import PyGattBackend

#try:
#    from unittest import mock
#except:
#    import mock


def test_dummy():
    assert True


