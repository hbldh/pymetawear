# -*- coding: utf-8 -*-
"""Release data for the PyMetaWear project."""

# -----------------------------------------------------------------------------
#  Copyright (c) 2016, Nedomkull Mathematical Modeling AB.
# -----------------------------------------------------------------------------

import os
from ctypes import cdll

# Version information.
__version__ = '0.3.0'
version = __version__  # backwards compatibility name
version_info = (0, 3, 0)

if os.environ.get('METAWEAR_LIB_SO_NAME') is not None:
    libmetawear = cdll.LoadLibrary(os.environ["METAWEAR_LIB_SO_NAME"])
else:
    libmetawear = cdll.LoadLibrary(
        os.path.join(os.path.abspath(os.path.dirname(__file__)),
                     'libmetawear.so'))







