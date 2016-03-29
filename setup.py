#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
The setup script for the Mt. Black library.

.. moduleauthor:: hbldh <henrik.blidh@swedwise.com>

Created on 2014-02-14, 16:20

"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

from setuptools import setup, find_packages
import pymetawear


install_requires = [
    'pybluez[ble]>=0.22',
    'gattlib>=0.20150805'
]

LONG_DESCRIPTION = """
PyMetaWear is a library for connecting and communicating with a MetaWear board.
"""

setup(
    name='pymetawear',
    version=pymetawear.__version__,
    author=pymetawear.author,
    author_email=pymetawear.author_email,
    maintainer=pymetawear.maintainer,
    maintainer_email=pymetawear.maintainer_email,
    url=pymetawear.url,
    download_url=pymetawear.download_url,
    description=pymetawear.description,
    long_description=LONG_DESCRIPTION,
    license=pymetawear.license,
    platforms=pymetawear.platforms,
    keywords=pymetawear.keywords,
    classifiers=pymetawear.classifiers,
    packages=find_packages(),
    package_data={},
    install_requires=install_requires,
    dependency_links=[],
    ext_modules=[],
    entry_points={
    }
)
