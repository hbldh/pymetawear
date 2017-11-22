# -*- coding: utf-8 -*-
"""Release data for the PyMetaWear project."""

# -----------------------------------------------------------------------------
#  Copyright (c) 2017, Henrik Blidh
# -----------------------------------------------------------------------------

import sys

from mbientlab.metawear import libmetawear

from pymetawear.version import __version__, version  # flake8: noqa

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
