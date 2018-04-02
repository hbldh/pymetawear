#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
exceptions
----------

Created by hbldh <henrik.blidh@nedomkull.com> on 2016-03-30

"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import


class PyMetaWearException(Exception):
    """Main exception."""
    pass


class PyMetaWearConnectionTimeout(PyMetaWearException):
    """Connection could not be established in time."""
    pass
