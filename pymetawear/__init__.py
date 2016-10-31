# -*- coding: utf-8 -*-
"""Release data for the PyMetaWear project."""

# -----------------------------------------------------------------------------
#  Copyright (c) 2016, Nedomkull Mathematical Modeling AB.
# -----------------------------------------------------------------------------

import os
import sys
import platform
import glob
from ctypes import cdll

from pymetawear.mbientlab.metawear.core import Fn_DataPtr, Fn_VoidPtr_Int
from pymetawear.mbientlab.metawear.functions import setup_libmetawear

# Logging solution inspired by Hitchhiker's Guide to Python and Requests
# Set default logging handler to avoid "No handler found" warnings.
import logging
try:  # Python 2.7+
    from logging import NullHandler
except ImportError:
    class NullHandler(logging.Handler):
        def emit(self, record):
            pass

logging.getLogger(__name__).addHandler(NullHandler())

# Version information.
__version__ = '0.6.0'
version = __version__  # backwards compatibility name
version_info = (0, 6, 0)

# Find and import the built MetaWear-CPP shared library.
if os.environ.get('METAWEAR_LIB_SO_NAME') is not None:
    libmetawear = cdll.LoadLibrary(os.environ["METAWEAR_LIB_SO_NAME"])
else:
    if platform.uname()[0] == 'Windows':
        dll_files = list(glob.glob(os.path.join(os.path.abspath(
            os.path.dirname(__file__)), 'MetaWear.*.dll')))
        shared_lib_file_name = dll_files[0]
    else:
        shared_lib_file_name = 'libmetawear.so'
    libmetawear = cdll.LoadLibrary(
        os.path.join(os.path.abspath(os.path.dirname(__file__)),
                     shared_lib_file_name))

setup_libmetawear(libmetawear)


def add_stream_logger(stream=sys.stdout, level=logging.DEBUG):
    """
    Helper for quickly adding a StreamHandler to the logger. Useful for
    debugging.
    Returns the handler after adding it.
    """
    logger = logging.getLogger(__name__)
    handler = logging.StreamHandler(stream=stream)
    handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
    logger.addHandler(handler)
    logger.setLevel(level)
    logger.debug('Added a {0} logging handler to logger: {1}'.format(stream.name, __name__))
    return handler
