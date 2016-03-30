# -*- coding: utf-8 -*-
"""Release data for the PyMetaWear project."""

# -----------------------------------------------------------------------------
#  Copyright (c) 2016, Nedomkull Mathematical Modeling AB.
# -----------------------------------------------------------------------------

# Version information.
# An empty _version_extra corresponds to a full release.
# 'dev' as a _version_extra string means this is a development version.
_version_major = 0
_version_minor = 1
_version_patch = 0
#_version_extra = 'dev3'
#_version_extra = 'alpha'
_version_extra = ''

# Construct full version string from these.
_ver = [_version_major, _version_minor, _version_patch]

__version__ = '.'.join(map(str, _ver))
if _version_extra:
    __version__ = __version__ + '.' + str(_version_extra)

version = __version__  # backwards compatibility name
version_info = (_version_major, _version_minor, _version_patch, _version_extra)








