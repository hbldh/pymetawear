#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""

.. moduleauthor:: hbldh <henrik.blidh@swedwise.com>

Created on 2016-04-08, 14:01

"""

from __future__ import division
from __future__ import print_function
# from __future__ import unicode_literals
from __future__ import absolute_import

import platform


IS_64_BIT = platform.architecture()[0] == '64bit'


try:
    # Python 2
    range_ = xrange
    string_types = (basestring, )

    def bytearray_to_str(ba):
        return str(ba)

except NameError:
    # Python 3
    range_ = range
    string_types = (str, )

    def bytearray_to_str(ba):
        if isinstance(ba, string_types):
            # PyBluez
            return ba.encode()
        else:
            # PyGatt
            return bytes([x for x in ba])



