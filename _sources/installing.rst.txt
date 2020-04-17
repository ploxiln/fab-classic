==========
Installing
==========

**fab-classic** is best installed via `pip <http://pip-installer.org>`_

    $ pip install fab-classic

Make sure that "Fabric" and "paramiko" packages are removed first, if you happen
to have previously installed them (because *fab-classic* depends on *Paramiko-NG*).

If you are upgrading *fab-classic* from version 1.15.x to version 1.16 or later,
then you do have "paramiko" installed as a dependency for fab-classic 1.15.x,
and you should uninstall it first::

    $ pip uninstall paramiko

It is also possible to install *fab-classic* such that it requires "paramiko"
instead of "paramiko-ng"::

    PARAMIKO_REPLACE=1 pip install --no-binary fab-classic fab-classic==1.18.0

(*paramiko-ng* also supports ``PARAMIKO_REPLACE``,
see `paramiko-ng#installation <https://github.com/ploxiln/paramiko-ng/#installation>`_)

Advanced users wanting to install a development version may use ``pip`` to grab
the latest master branch (as well as the dev version of the Paramiko-NG dependency)::

    $ pip install -e git+https://github.com/ploxiln/paramiko-ng/#egg=paramiko-ng
    $ pip install -e git+https://github.com/ploxiln/fab-classic/#egg=fab-classic


Dependencies
============

In order for Fabric's installation to succeed, you will need three primary pieces of software:

* the Python programming language version 2.7, or version 3.4, or a later 3.x release;
* the ``setuptools`` packaging/installation library;
* and the Python `Paramiko-NG <https://github.com/ploxiln/paramiko-ng>`_ SSH library.
  See the `Paramiko installation docs <https://github.com/ploxiln/paramiko-ng#installation>`_ for more info.

setuptools
----------

`Setuptools`_ comes with some Python installations by default; if yours doesn't,
you'll need to grab it. In such situations it's typically packaged as
``python-setuptools``, ``py27-setuptools`` or similar.

.. _setuptools: https://pypi.org/project/setuptools/

Development dependencies
------------------------

If you are interested in doing development work on Fabric (or even just running
the test suite), you may also need to install some or all of the following
packages:

* `git <http://git-scm.com>`_ in order to obtain some of the other dependencies below;
* `Nose <https://github.com/nose-devs/nose>`_
* `Fudge <http://farmdev.com/projects/fudge/index.html>`_
* `Sphinx <http://sphinx.pocoo.org/>`_

For an up-to-date list of exact testing/development requirements, including
version numbers, please see the ``dev-requirements.txt`` file included with the
source distribution. This file is intended to be used with ``pip``, e.g.
``pip install -r dev-requirements.txt``.


.. _downloads:

Downloads
=========

To obtain a tar.gz or zip archive of the Fabric source code, you may visit
`Fabric's PyPI page <http://pypi.python.org/pypi/fab-classic>`_, which offers manual
downloads in addition to being the entry point for ``pip``


.. _source-code-checkouts:

Source code checkouts
=====================

The Fabric developers manage the project's source code with the `Git
<http://git-scm.com>`_ DVCS. To follow Fabric's development via Git instead of
downloading official releases, you have the following options:

* Clone the canonical repository straight from `the Fabric organization's
  repository on Github <https://github.com/ploxiln/fab-classic>`_,
  ``git://github.com/ploxiln/fab-classic.git``
* Make your own fork of the Github repository by making a Github account,
  visiting `ploxiln/fab-classic <http://github.com/ploxiln/fab-classic>`_ and clicking the
  "fork" button.

.. note::

    If you've obtained the Fabric source via source control and plan on
    updating your checkout in the future, we highly suggest using ``python
    setup.py develop`` instead -- it will use symbolic links instead of file
    copies, ensuring that imports of the library or use of the command-line
    tool will always refer to your checkout.
