#!/usr/bin/env python
from setuptools import setup, find_packages

from fabric.version import get_version


long_description = open("README.rst").read()


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
    packages=find_packages(),
    test_suite='nose.collector',
    tests_require=['nose<2.0', 'fudge<1.0', 'jinja2<3.0'],
    install_requires=['paramiko-ng', 'six>=1.10.0'],
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
        'Operating System :: Unix',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Software Development',
        'Topic :: Software Development :: Build Tools',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Clustering',
        'Topic :: System :: Software Distribution',
        'Topic :: System :: Systems Administration',
    ],
)
