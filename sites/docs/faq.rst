================================
Frequently Asked Questions (FAQ)
================================

These are some of the most commonly encountered problems or frequently asked
questions which we receive from users. They aren't intended as a substitute for
reading the rest of the documentation, especially the :ref:`usage docs
<usage-docs>`, so please make sure you check those out if your question is not
answered here.


Fabric installs but doesn't run!
================================

On systems with old versions of ``setuptools`` (notably OS X Mavericks [10.9]
as well as older Linux distribution versions) users frequently have problems
running Fabric's binary scripts; this is because these ``setuptools`` are too
old to deal with the modern distribution formats Fabric and some of its
dependencies may use.

One method we've used to recreate this error:

* OS X 10.9 using system Python
* Pip obtained via e.g. ``sudo easy_install pip`` or ``sudo python get-pip.py``
* ``pip install fabric``
* ``fab [args]`` then results in the following traceback::

    Traceback (most recent call last):
      File "/usr/local/bin/fab", line 5, in <module>
        from pkg_resources import load_entry_point
      File "/System/Library/Frameworks/Python.framework/Versions/2.7/Extras/lib/python/pkg_resources.py", line 2603, in <module>
        working_set.require(__requires__)
      File "/System/Library/Frameworks/Python.framework/Versions/2.7/Extras/lib/python/pkg_resources.py", line 666, in require
        needed = self.resolve(parse_requirements(requirements))
      File "/System/Library/Frameworks/Python.framework/Versions/2.7/Extras/lib/python/pkg_resources.py", line 565, in resolve
        raise DistributionNotFound(req)  # XXX put more info here
    pkg_resources.DistributionNotFound: paramiko>=1.10

The best solution is to obtain a newer ``setuptools`` (which fixes this bug
among many others) like so::

    $ sudo pip install -U setuptools

Uninstalling, then reinstalling Fabric after doing so should fix the issue.

Another approach is to tell ``pip`` not to use the ``wheel`` format (make sure
you've already uninstalled Fabric and Paramiko beforehand)::

    $ sudo pip install fabric --no-use-wheel

Finally, you may also find success by using a different Python
interpreter/ecosystem, such as that provided by `Homebrew <http://brew.sh>`_
(`specific Python doc page
<https://github.com/Homebrew/homebrew/wiki/Homebrew-and-Python>`_).


How do I dynamically set host lists?
====================================

See :ref:`dynamic-hosts`.


How can I run something after my task is done on all hosts?
===========================================================

See :ref:`leveraging-execute-return-value`.


.. _init-scripts-pty:

Init scripts don't work!
========================

Init-style start/stop/restart scripts (e.g. ``/etc/init.d/apache2 start``)
sometimes don't like Fabric's allocation of a pseudo-tty, which is active by
default. In almost all cases, explicitly calling the command in question with
``pty=False`` works correctly::

    sudo("/etc/init.d/apache2 restart", pty=False)

If you have no need for interactive behavior and run into this problem
frequently, you may want to deactivate pty allocation globally by setting
:ref:`env.always_use_pty <always-use-pty>` to ``False``.

.. _one-shell-per-command:

My (``cd``/``workon``/``export``/etc) calls don't seem to work!
===============================================================

While Fabric can be used for many shell-script-like tasks, there's a slightly
unintuitive catch: each `~fabric.operations.run` or `~fabric.operations.sudo`
call has its own distinct shell session. This is required in order for Fabric
to reliably figure out, after your command has run, what its standard out/error
and return codes were.

Unfortunately, it means that code like the following doesn't behave as you
might assume::

    def deploy():
        run("cd /path/to/application")
        run("./update.sh")

If that were a shell script, the second `~fabric.operations.run` call would
have executed with a current working directory of ``/path/to/application/`` --
but because both commands are run in their own distinct session over SSH, it
actually tries to execute ``$HOME/update.sh`` instead (since your remote home
directory is the default working directory).

A simple workaround is to make use of shell logic operations such as ``&&``,
which link multiple expressions together (provided the left hand side executed
without error) like so::

    def deploy():
        run("cd /path/to/application && ./update.sh")

Fabric provides a convenient shortcut for this specific use case, in fact:
`~fabric.context_managers.cd`. There is also `~fabric.context_managers.prefix`
for arbitrary prefix commands.

.. note::
    You might also get away with an absolute path and skip directory changing
    altogether::

        def deploy():
            run("/path/to/application/update.sh")

    However, this requires that the command in question makes no assumptions
    about your current working directory!


How do I use ``su`` to run commands as another user?
====================================================

This is a special case of :ref:`one-shell-per-command`. As that FAQ explains,
commands like ``su`` which are 'stateful' do not work well in Fabric, so
workarounds must be used.

In the case of running commands as a user distinct from the login user, you
have two options:

#. Use `~fabric.operations.sudo` with its ``user=`` kwarg, e.g.
   ``sudo("command", user="otheruser")``. If you want to factor the ``user``
   part out of a bunch of commands, use `~fabric.context_managers.settings` to
   set ``env.sudo_user``::

       with settings(sudo_user="otheruser"):
           sudo("command 1")
           sudo("command 2")
           ...

#. If your target system cannot use ``sudo`` for some reason, you can still use
   ``su``, but you need to invoke it in a non-interactive fashion by telling it
   to run a specific command instead of opening a shell. Typically this is the
   ``-c`` flag, e.g. ``su otheruser -c "command"``.

   To run multiple commands in the same ``su -c`` "wrapper", you could e.g.
   write a wrapper function around `~fabric.operations.run`::

       def run_su(command, user="otheruser"):
           return run('su %s -c "%s"' % (user, command))


Why do I sometimes see ``err: stdin: is not a tty``?
====================================================

This message is typically generated by programs such as ``biff`` or ``mesg``
lurking within your remote user's ``.profile`` or ``.bashrc`` files (or any
other such files, including system-wide ones.) Fabric's default mode of
operation involves executing the Bash shell in "login mode", which causes these
files to be executed.

Because Fabric also doesn't bother asking the remote end for a tty by default
(as it's not usually necessary) programs fired within your startup files, which
expect a tty to be present, will complain -- and thus, stderr output about
"stdin is not a tty" or similar.

There are multiple ways to deal with this problem:

* Find and remove or comment out the offending program call. If the program was
  not added by you on purpose and is simply a legacy of the operating system,
  this may be safe to do, and is the simplest approach.
* Override ``env.shell`` to remove the ``-l`` flag. This should tell Bash not
  to load your startup files. If you don't depend on the contents of your
  startup files (such as aliases or whatnot) this may be a good solution.
* Pass ``pty=True`` to `run` or `sudo`, which will force allocation of a
  pseudo-tty on the remote end, and hopefully cause the offending program to be
  less cranky.


.. _faq-daemonize:

Why can't I run programs in the background with ``&``? It makes Fabric hang.
============================================================================

Because Fabric executes a shell on the remote end for each invocation of
``run`` or ``sudo`` (:ref:`see also <one-shell-per-command>`), backgrounding a
process via the shell will not work as expected. Backgrounded processes may
still prevent the calling shell from exiting until they stop running, and this
in turn prevents Fabric from continuing on with its own execution.

The key to fixing this is to ensure that your process' standard pipes are all
disassociated from the calling shell, which may be done in a number of ways
(listed in order of robustness):

* Use a pre-existing daemonization technique if one exists for the program at
  hand -- for example, calling an init script instead of directly invoking a
  server binary.

    * Or leverage a process manager such as ``supervisord``, ``upstart`` or
      ``systemd`` - such tools let you define what it means to "run" one of
      your background processes, then issue init-script-like
      start/stop/restart/status commands. They offer many advantages over
      classic init scripts as well.

* Use ``tmux``, ``screen`` or ``dtach`` to fully detach the process from the
  running shell; these tools have the benefit of allowing you to reattach to
  the process later on if needed (though they are more ad-hoc than
  ``supervisord``-like tools).
* You *may* be able to the program under ``nohup`` or similar "in-shell" tools
  - however we strongly recommend the prior approaches because ``nohup`` has
  only worked well for a minority of our users.


.. _faq-bash:

My remote system doesn't have ``bash`` installed by default, do I need to install ``bash``?
===========================================================================================

While Fabric is written with ``bash`` in mind, it's not an absolute
requirement.  Simply change :ref:`env.shell <shell>` to call your desired shell, and
include an argument similar to ``bash``'s ``-c`` argument, which allows us to
build shell commands of the form::

    /bin/bash -l -c "<command string here>"

where ``/bin/bash -l -c`` is the default value of :ref:`env.shell <shell>`.

.. note::

    The ``-l`` argument specifies a login shell and is not absolutely
    required, merely convenient in many situations. Some shells lack the option
    entirely and it may be safely omitted in such cases.

A relatively safe baseline is to call ``/bin/sh``, which may call the original
``sh`` binary, or (on some systems) ``csh``, and give it the ``-c``
argument, like so::

    from fabric.api import env

    env.shell = "/bin/sh -c"

This has been shown to work on FreeBSD and may work on other systems as well.


.. _faq-csh:

I use ``csh`` remotely and keep getting errors about ``Unmatched ".``.
======================================================================

If the remote host uses ``csh`` for your login shell, Fabric requires the shell
variable ``backslash_quote`` to be set, or else any quote-escaping Fabric does
will not work. For example, add the following line to ``~/.cshrc``::

    set backslash_quote


I'm sometimes incorrectly asked for a passphrase instead of a password.
=======================================================================

Due to a bug of sorts in our SSH layer, it's not currently possible for Fabric
to always accurately detect the type of authentication needed. We have to try
and guess whether we're being asked for a private key passphrase or a remote
server password, and in some cases our guess ends up being wrong.

The most common such situation is where you, the local user, appear to have an
SSH keychain agent running, but the remote server is not able to honor your SSH
key, e.g. you haven't yet transferred the public key over or are using an
incorrect username. In this situation, Fabric will prompt you with "Please
enter passphrase for private key", but the text you enter is actually being
sent to the remote end's password authentication.

We hope to address this in future releases by modifying a fork of the
aforementioned SSH library.


Is Fabric thread-safe?
======================

Currently, no, it's not -- Fabric-1.x and fab-classic rely heavily on
shared state in order to keep the codebase simple. For a re-design
that fixes this, check out `Fabric-2.x <https://github.com/fabric/fabric>`_
