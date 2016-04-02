#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
The setup script for the Mt. Black library.

.. moduleauthor:: hbldh <henrik.blidh@swedwise.com>

Created on 2014-02-14, 16:20

'''

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import os
import sys
import subprocess
import shutil
import re
from codecs import open

from setuptools import setup, find_packages

import pymetawear


def read(f):
    return open(f, encoding='utf-8').read()


basedir = os.path.abspath(os.path.dirname(__file__))
path_to_libmetawear_so = os.path.join(
    basedir, 'pymetawear', 'Metawear-CppAPI', 'dist', 'release', 'lib',
    'x64' if os.uname()[-1] == 'x86_64' else 'x86', 'libmetawear.so')
path_to_metawear_python_wrappers = os.path.join(basedir, 'pymetawear', 'Metawear-CppAPI', 'wrapper', 'python')

print('Running git submodule init...')
p = subprocess.Popen(['git', 'submodule', 'init'], cwd=basedir, stdout=sys.stdout, stderr=sys.stderr)
p.communicate()
print('Running git submodule update...')
p = subprocess.Popen(['git', 'submodule', 'update'], cwd=basedir, stdout=sys.stdout, stderr=sys.stderr)
p.communicate()

print('Make build...')
p = subprocess.Popen(['make', 'clean'], cwd=os.path.join(basedir, 'pymetawear', 'Metawear-CppAPI'),
                     stdout=sys.stdout, stderr=sys.stderr)
p.communicate()
p = subprocess.Popen(['make', 'build'], cwd=os.path.join(basedir, 'pymetawear', 'Metawear-CppAPI'),
                     stdout=sys.stdout, stderr=sys.stderr)
p.communicate()

# Copy the built shared library to pymetawear folder.
shutil.copy(os.path.join(basedir, 'pymetawear', 'Metawear-CppAPI', 'dist', 'release', 'lib',
            'x64' if os.uname()[-1] == 'x86_64' else 'x86', 'libmetawear.so'),
            os.path.join(basedir, 'pymetawear', 'libmetawear.so'))
# Copy the Mbientlab Python wrappers to pymetawear folder. First create folders if needed.
try:
    os.makedirs(os.path.join(basedir, 'pymetawear', 'mbientlab'))
except:
    pass

try:
    os.makedirs(os.path.join(basedir, 'pymetawear', 'mbientlab', 'metawear'))
except:
    pass
with open(os.path.join(basedir, 'pymetawear', 'mbientlab', '__init__.py'), 'w') as f:
    f.write("#!/usr/bin/env python\n# -*- coding: utf-8 -*-")
with open(os.path.join(basedir, 'pymetawear', 'mbientlab', 'metawear', '__init__.py'), 'w') as f:
    f.write("#!/usr/bin/env python\n# -*- coding: utf-8 -*-")
shutil.copy(os.path.join(path_to_metawear_python_wrappers, 'mbientlab', 'metawear', 'core.py'),
            os.path.join(basedir, 'pymetawear', 'mbientlab', 'metawear', 'core.py'))
shutil.copy(os.path.join(path_to_metawear_python_wrappers, 'mbientlab', 'metawear', 'peripheral.py'),
            os.path.join(basedir, 'pymetawear', 'mbientlab', 'metawear', 'peripheral.py'))
shutil.copy(os.path.join(path_to_metawear_python_wrappers, 'mbientlab', 'metawear', 'processor.py'),
            os.path.join(basedir, 'pymetawear', 'mbientlab', 'metawear', 'processor.py'))
shutil.copy(os.path.join(path_to_metawear_python_wrappers, 'mbientlab', 'metawear', 'sensor.py'),
            os.path.join(basedir, 'pymetawear', 'mbientlab', 'metawear', 'sensor.py'))


with open('pymetawear/__init__.py', 'r') as fd:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
                        fd.read(), re.MULTILINE).group(1)


setup(
    name='pymetawear',
    version=version,
    author='Henrik Blidh',
    author_email='henrik.blidh@nedobmkull.com',
    url='https://github.com/hbldh/pymetawear',
    description='Python Lib for connecting to and using MetaWear boards.',
    long_description=read('README.rst') + '\n\n' + read('HISTORY.rst'),
    license='MIT',
    platforms=['Linux'],
    keywords=['Bluetooth', 'IMU', 'MetaWear', 'Mbientlab'],
    classifiers=[
        'Programming Language :: Python :: 2.7',
        'Operating System :: POSIX :: Linux',
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
    ],
    packages=find_packages(exclude=['tests', 'docs']),
    package_data={
        'pymetawear': ['libmetawear.so'],
    },
    install_requires=[
        'gattlib>=0.20150805'
    ],
    extras_require={
        'pygatt': ["pygatt>=2.0.1"],
    },
    dependency_links=[],
    ext_modules=[],
    entry_points={
    }
)
