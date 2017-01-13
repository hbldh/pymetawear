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

from pymetawear.version import __version__, version  # flake8: noqa
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


# Find and import the built MetaWear-CPP shared library.
if os.environ.get('METAWEAR_LIB_SO_NAME') is not None:
    METAWEAR_LIB_SO_NAME = os.environ["METAWEAR_LIB_SO_NAME"]
else:
    if platform.uname()[0] == 'Windows':
        dll_files = list(glob.glob(os.path.join(os.path.abspath(
            os.path.dirname(__file__)), 'MetaWear.*.dll')))
        METAWEAR_LIB_SO_NAME = dll_files[0]
    else:
        METAWEAR_LIB_SO_NAME = 'libmetawear.so'
    METAWEAR_LIB_SO_NAME = os.path.join(os.path.abspath(
        os.path.dirname(__file__)), METAWEAR_LIB_SO_NAME)
libmetawear = cdll.LoadLibrary(METAWEAR_LIB_SO_NAME)
setup_libmetawear(libmetawear)


def add_stream_logger(stream=sys.stdout, level=logging.DEBUG):
    """
    Helper for quickly adding a StreamHandler to the logger. Useful for
    debugging.
    Returns the handler after adding it.
    """
    logger = logging.getLogger(__name__)
    has_stream_handler = any([isinstance(hndl, logging.StreamHandler) for hndl in logger.handlers])
    if has_stream_handler:
        return logger.handlers[-1]
    handler = logging.StreamHandler(stream=stream)
    handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
    logger.addHandler(handler)
    logger.setLevel(level)
    logger.debug('Added a {0} logging handler to logger: {1}'.format(stream.name, __name__))
    return handler
