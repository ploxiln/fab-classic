===============
Troubleshooting
===============

Stuck? Having a problem? Here are the steps to try before you submit a bug
report.

* **Make sure Fabric is really the problem.** If your problem is in the
  behavior or output of a remote command, try recreating it without Fabric
  involved:

    * Run Fabric with ``--show=debug`` and look for the ``run:`` or ``sudo:``
      line about the command in question. Try running that exact command,
      including any ``/bin/bash`` wrapper, remotely and see what happens. This
      may find problems related to the bash or sudo wrappers.
    * Execute the command (both the normal version, and the 'unwrapped' version
      seen via ``--show=debug``) from your local workstation using ``ssh``,
      e.g.::

          $ ssh -t mytarget "my command"

      The ``-t`` flag matches Fabric's default behavior of enabling a PTY
      remotely. This helps identify apps that behave poorly when run in a
      non-shell-spawned PTY.

* **Enable Paramiko-level debug logging.** If your issue is in the lower level
  Paramiko library, it can help us to see the debug output Paramiko prints. At
  top level in your fabfile, add the following::

      import logging
      logging.basicConfig(level=logging.DEBUG)

  This should start printing Paramiko's debug statements to your standard error
  stream. (Feel free to add more logging kwargs to ``basicConfig()`` such as
  ``filename='/path/to/a/file'`` if you like.)
