#!/usr/bin/env python
from setuptools import setup, find_packages

from fabric.version import get_version


with open('README.rst') as f:
    readme = f.read()

long_description = """
To find out what's new in this version of Fabric, please see `the changelog
<http://fabfile.org/changelog-v1.html>`_.

You can also install the `development version via ``pip install -e
git+https://github.com/ploxiln/fab-classic/#egg=fab-classic``.

----

%s

----

For more information, please see the Fabric website or execute ``fab --help``.
""" % (readme)


setup(
    name='fab-classic',
    version=get_version('short'),
    description='fab-classic is a simple, Pythonic tool for remote execution and deployment.',
    long_description=long_description,
    author='Pierce Lopez',
    author_email='pierce.lopez@gmail.com',
    url='https://github.com/ploxiln/fab-classic',
    packages=find_packages(),
    test_suite='nose.collector',
    tests_require=['nose<2.0', 'fudge<1.0', 'jinja2<3.0'],
    install_requires=['paramiko>=1.10,<3.0'],
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
          'Programming Language :: Python :: 2 :: Only',
          'Programming Language :: Python :: 2.7',
          'Topic :: Software Development',
          'Topic :: Software Development :: Build Tools',
          'Topic :: Software Development :: Libraries',
          'Topic :: Software Development :: Libraries :: Python Modules',
          'Topic :: System :: Clustering',
          'Topic :: System :: Software Distribution',
          'Topic :: System :: Systems Administration',
    ],
)
