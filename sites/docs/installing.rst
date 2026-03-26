==========
Installing
==========

**fab-classic** can be installed with `pip <http://pip-installer.org>`_

    pip install fab-classic

Make sure that the original "Fabric" package is removed first.

As of *fab-classic* 1.21 it depends on the original *paramiko* package,
previous versions depended on *paramiko-ng* instead. If you are switching
between *paramiko* and *paramiko-ng* in an existing "python environment"
(perhaps due to upgrading *fab-classic*) be sure to uninstall any existing
paramiko variant before a different one is installed.

It is also possible to install *fab-classic* such that it requires "paramiko-ng"
instead of the original "paramiko"::

    PARAMIKO_REPLACE=1 pip install --no-binary fab-classic fab-classic==1.21.0

(This is opposite of how ``PARAMIKO_REPLACE`` worked for older versions of *fab-classic*.)

*paramiko-ng* also supports ``PARAMIKO_REPLACE``, see
`paramiko-ng#installation <https://github.com/ploxiln/paramiko-ng/#installation>`_


Dependencies
============

In order for Fabric's installation to succeed, you will need three primary pieces of software:

* Python version 3.5 or later;
* the ``setuptools`` packaging/installation library;
* and the Python `Paramiko <https://www.paramiko.org/>`_ or
  `Paramiko-NG <https://github.com/ploxiln/paramiko-ng>`_ SSH library.
  (Paramiko has its own dependencies, see its own documentation for details.)

setuptools
----------

`Setuptools`_ comes with some Python installations by default; if yours doesn't,
you'll need to grab it. In such situations it's typically packaged as
``python-setuptools``, ``py27-setuptools`` or similar.

.. _setuptools: https://pypi.org/project/setuptools/

Development dependencies
------------------------

If you are interested in doing development work on Fabric (or even just running
the test suite), you may also need to install some additional packages, listed
in ``dev-requirements.txt`` (including primarily "Nose" and "Fudge"):

    pip install -r dev-requirements.txt

To build the documentation with "Sphinx", you'll need the dependencies in
``doc-requirements.txt``:

    pip install -r doc-requirements.txt


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

* Clone the canonical repository straight from the `repository on Github
  <https://github.com/ploxiln/fab-classic>`_, ``git://github.com/ploxiln/fab-classic.git``
* Make your own fork of the Github repository by making a Github account,
  visiting `ploxiln/fab-classic <http://github.com/ploxiln/fab-classic>`_ and clicking the
  "fork" button.

.. note::

    If you've obtained the Fabric source via source control and plan on
    updating your checkout in the future, we highly suggest using ``python
    setup.py develop`` instead -- it will use symbolic links instead of file
    copies, ensuring that imports of the library or use of the command-line
    tool will always refer to your checkout.
