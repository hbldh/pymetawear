# -*- coding: utf-8 -*-
"""Release data for the PyMetaWear project."""

# -----------------------------------------------------------------------------
#  Copyright (c) 2016, Nedomkull Mathematical Modeling AB.
# -----------------------------------------------------------------------------

import os
from ctypes import cdll, c_long
from pymetawear.mbientlab.metawear.core import FnDataPtr, FnVoid
from pymetawear.mbientlab.metawear.functions import setup_libmetawear
from pymetawear.utils import IS_64_BIT

# Version information.
__version__ = '0.4.5.dev1'
version = __version__  # backwards compatibility name
version_info = (0, 4, 5, 'dev1')

if os.environ.get('METAWEAR_LIB_SO_NAME') is not None:
    libmetawear = cdll.LoadLibrary(os.environ["METAWEAR_LIB_SO_NAME"])
else:
    libmetawear = cdll.LoadLibrary(
        os.path.join(os.path.abspath(os.path.dirname(__file__)),
                     'libmetawear.so'))

setup_libmetawear(libmetawear)

# Alleviating Segfault causing pointer errors in 64-bit Python.
if IS_64_BIT:
    libmetawear.mbl_mw_datasignal_subscribe.argtypes = [c_long, FnDataPtr]
    libmetawear.mbl_mw_datasignal_unsubscribe.argtypes = [c_long, ]
    libmetawear.mbl_mw_datasignal_log.argtypes = [c_long, FnDataPtr, FnVoid]
    libmetawear.mbl_mw_datasignal_remove_logger.argtypes = [c_long, ]







