"""
Fabric's own fabfile.
"""

import nose

from fabric.api import task


@task(default=True)
def test(args=None):
    """
    Run all unit tests and doctests.

    Specify string argument ``args`` for additional args to ``nosetests``.
    """
    # Default to explicitly targeting the 'tests' folder, but only if nothing
    # is being overridden.
    tests = "" if args else " tests"
    default_args = "-sv --nologcapture %s" % tests  # --with-doctest broke ?
    default_args += (" " + args) if args else ""
    nose.core.run_exit(argv=[''] + default_args.split())
