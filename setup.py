#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
The setup script for the PyMetaWear package.

.. moduleauthor:: hbldh <henrik.blidh@nedomkull.com>

Created on 2016-04-08

'''

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import os
import sys
import subprocess
import shutil
import re
import glob
from codecs import open

from setuptools import setup, find_packages
from setuptools.command import build_py, develop


class PyMetaWearDeveloper(develop.develop):
    def run(self):
        build_solution()
        develop.develop.run(self)


class PyMetaWearBuilder(build_py.build_py):
    def run(self):
        build_solution()
        build_py.build_py.run(self)


def build_solution():
    # Establish source paths.
    basedir = os.path.abspath(os.path.dirname(__file__))
    pkg_dir = os.path.join(basedir, 'pymetawear')

    arch = os.uname()[-1]
    if arch in ('x86_64', 'amd64'):
        dist_dir = 'x64'
    elif arch == 'armv7l':
        dist_dir = 'arm'
    else:
        dist_dir = 'x86'

    path_to_dist_dir = os.path.join(
        pkg_dir, 'Metawear-CppAPI', 'dist', 'release', 'lib', dist_dir)
    path_to_metawear_python_wrappers = os.path.join(
        pkg_dir, 'Metawear-CppAPI', 'wrapper', 'python')

    # Git submodule init
    p = subprocess.Popen(['git', 'submodule', 'init'],
                         cwd=basedir, stdout=sys.stdout, stderr=sys.stderr)
    p.communicate()

    # Git submodule update
    p = subprocess.Popen(['git', 'submodule', 'update'],
                         cwd=basedir, stdout=sys.stdout, stderr=sys.stderr)
    p.communicate()

    constants_h_file = os.path.join(
        pkg_dir, 'Metawear-CppAPI', 'src', 'metawear',
        'core', 'cpp', 'constant.h')
    with open(constants_h_file, 'rt') as f:
        t = f.read()
    t = t.replace('TIME_PER_COMMAND = 150', 'TIME_PER_COMMAND = 300')
    with open(constants_h_file, 'wt') as f:
        f.write(t)

    # Run make file for MetaWear-CppAPI
    p = subprocess.Popen(
        ['make', 'clean'],
        cwd=os.path.join(pkg_dir, 'Metawear-CppAPI'),
        stdout=sys.stdout, stderr=sys.stderr)
    p.communicate()
    p = subprocess.Popen(
        ['make', 'build'],
        cwd=os.path.join(pkg_dir, 'Metawear-CppAPI'),
        stdout=sys.stdout, stderr=sys.stderr)
    p.communicate()

    symlinks_to_create = []
    # Copy the built shared library to pymetawear folder.
    for dist_file in glob.glob(path_to_dist_dir + "/libmetawear.*"):
        print(dist_file)
        if os.path.islink(dist_file):
            symlinks_to_create.append(
                (os.path.basename(os.readlink(dist_file)),
                os.path.basename(dist_file)))
        else:
            shutil.copy(dist_file, os.path.join(
                pkg_dir, os.path.basename(dist_file)))

    for symlink_src, symlink_dest in symlinks_to_create:
        os.symlink(symlink_src, os.path.join(pkg_dir, symlink_dest))

    # Copy the Mbientlab Python wrappers to pymetawear folder.
    # First create folders if needed.
    try:
        os.makedirs(os.path.join(pkg_dir, 'mbientlab', 'metawear'))
    except:
        pass

    init_files_to_create = [
        os.path.join(pkg_dir, 'mbientlab', '__init__.py'),
        os.path.join(pkg_dir, 'mbientlab', 'metawear', '__init__.py')
    ]
    for init_file in init_files_to_create:
        with open(init_file, 'w') as f:
            f.write("#!/usr/bin/env python\n# -*- coding: utf-8 -*-")

    # Copy all Python files from the MetWear C++ API Python wrapper
    for pth, _, pyfiles in os.walk(
            os.path.join(path_to_metawear_python_wrappers,
                         'mbientlab', 'metawear')):
        for py_file in filter(lambda x: os.path.splitext(x)[1] == '.py', pyfiles):
            try:
                shutil.copy(
                    os.path.join(pth, py_file),
                    os.path.join(pkg_dir, 'mbientlab', 'metawear', py_file))
            except:
                pass

with open('pymetawear/__init__.py', 'r') as fd:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
                        fd.read(), re.MULTILINE).group(1)


def read(f):
    return open(f, encoding='utf-8').read()


setup(
    name='pymetawear',
    version=version,
    author='Henrik Blidh',
    author_email='henrik.blidh@nedomkull.com',
    url='https://github.com/hbldh/pymetawear',
    description='Python Lib for connecting to and using MetaWear boards.',
    long_description=read('README.rst') + '\n\n' + read('HISTORY.rst'),
    license='MIT',
    platforms=['Linux'],
    keywords=['Bluetooth', 'IMU', 'MetaWear', 'MbientLab'],
    classifiers=[
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Operating System :: POSIX :: Linux',
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
    ],
    cmdclass={
        'build_py': PyMetaWearBuilder,
        'develop': PyMetaWearDeveloper
    },
    packages=find_packages(exclude=['tests', 'docs', 'examples']),
    # Adding MbientLab's Python code as package data since it is copied
    # to folder after ``find_packages`` is run.
    package_data={
        'pymetawear': [
            'libmetawear.so*',
            'mbientlab/*.py',
            'mbientlab/metawear/*.py'
        ],
    },
    install_requires=[
        'pybluez[ble]>=0.22',
        'pygatt[GATTTOOL]>=2.0.1',
        'pexpect>=4.2.0'
    ],
    extras_require={'bluepy': 'bluepy>=1.0.5'},
    ext_modules=[],
    entry_points={
    }
)
