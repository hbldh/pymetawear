#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Note: To use the 'upload' functionality of this file, you must:
#   $ pip install twine

import io
import os
import sys
import re
from shutil import rmtree

from setuptools import find_packages, setup, Command

# Package meta-data.
NAME = 'pymetawear'
DESCRIPTION = "Python client for connecting to MbientLab's MetaWear boards"
URL = 'https://github.com/hbldh/pymetawear'
EMAIL = 'henrik.blidh@nedomkull.com'
AUTHOR = 'Henrik Blidh'

# What packages are required for this module to be executed?
REQUIRED = [
    'metawear>=0.3.1'
]

# ------------------------------------------------

here = os.path.abspath(os.path.dirname(__file__))

# Import the README and HISTORY and use it as the long-description.
with io.open(os.path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = '\n' + f.read()
with io.open(os.path.join(here, 'HISTORY.rst'), encoding='utf-8') as f:
    long_description += '\n' + f.read()

about = {}
with io.open('pymetawear/version.py', 'r', encoding='utf-8') as fd:
    about['__version__'] = re.search(
        r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
        fd.read(), re.MULTILINE).group(1)


class UploadCommand(Command):
    """Support setup.py upload."""

    description = 'Build and publish the package.'
    user_options = []

    @staticmethod
    def status(s):
        """Prints things in bold."""
        print('\033[1m{0}\033[0m'.format(s))

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        try:
            self.status('Removing previous builds…')
            rmtree(os.path.join(here, 'dist'))
        except OSError:
            pass

        self.status('Building Source and Wheel (universal) distribution…')
        os.system('{0} setup.py sdist bdist_wheel --universal'.format(sys.executable))

        self.status('Uploading the package to PyPi via Twine…')
        os.system('twine upload dist/*')

        sys.exit()


setup(
    name=NAME,
    version=about['__version__'],
    description=DESCRIPTION,
    long_description=long_description,
    author=AUTHOR,
    author_email=EMAIL,
    url=URL,
    packages=find_packages(exclude=['tests', 'docs', 'examples', 'examples.*']),
    install_requires=REQUIRED,
    include_package_data=True,
    license='MIT',
    classifiers=[
        # Trove classifiers
        # Full list: https://pypi.python.org/pypi?%3Aaction=list_classifiers
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Operating System :: POSIX :: Linux',
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
    ],
    # $ setup.py publish support.
    cmdclass={
        'upload': UploadCommand,
    },
)
