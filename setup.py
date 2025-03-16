#!/usr/bin/env python
import os
from setuptools import setup

from fabric.version import get_version


long_description = open("README.rst").read()

# set PARAMIKO_REPLACE=1 to require "paramiko" instead of "paramiko-ng"
paramiko = 'paramiko' if os.environ.get('PARAMIKO_REPLACE') else 'paramiko-ng'

setup(
    name='fab-classic',
    version=get_version('short'),
    description='fab-classic is a simple, Pythonic tool for remote execution and deployment.',
    long_description=long_description,
    author='Jeff Forcier',
    author_email='jeff@bitprophet.org',
    maintainer='Pierce Lopez',
    maintainer_email='pierce.lopez@gmail.com',
    url='https://github.com/ploxiln/fab-classic',
    packages=['fabric', 'fabric.contrib'],
    python_requires=">=3.5",
    install_requires=[paramiko + '>=2.0'],
    entry_points={
        'console_scripts': [
            'fab = fabric.main:main',
        ]
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: BSD License',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX',
        'Operating System :: Unix',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Build Tools',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Clustering',
        'Topic :: System :: Systems Administration',
    ],
)
