import sys
import textwrap

from nose.tools import ok_, raises
from fudge import (Fake, patch_object, with_patched_object, patched_context,
                   with_fakes)

from fabric.context_managers import settings, hide, show
from fabric.network import (HostConnectionCache, join_host_strings, normalize,
                            denormalize, key_filenames, ssh, NetworkError, connect)
import fabric.network  # noqa: F401  # for patch_object()
import fabric.utils  # noqa: F401  # for patch_object()
from fabric.state import env, output, _get_system_username
from fabric.operations import run, sudo, prompt
from fabric.tasks import execute
from fabric.api import parallel

from mock_streams import mock_streams
from server import (server, RESPONSES, PASSWORDS, CLIENT_PRIVKEY, USER,
                    CLIENT_PRIVKEY_PASSPHRASE)
from utils import (
    FabricTest, aborts, assert_contains, eq_, match_, password_response, patched_input, support,
)


#
# Subroutines, e.g. host string normalization
#


class TestNetwork(FabricTest):
    def test_host_string_normalization(self):
        username = _get_system_username()
        for description, input, output_ in (
            ("Sanity check: equal strings remain equal",
                'localhost', 'localhost'),
            ("Empty username is same as get_system_username",
                'localhost', username + '@localhost'),
            ("Empty port is same as port 22",
                'localhost', 'localhost:22'),
            ("Both username and port tested at once, for kicks",
                'localhost', username + '@localhost:22'),
        ):
            eq_.description = "Host-string normalization: %s" % description
            yield eq_, normalize(input), normalize(output_)
            del eq_.description

    def test_normalization_for_ipv6(self):
        """
        normalize() will accept IPv6 notation and can separate host and port
        """
        username = _get_system_username()
        for description, input, output_ in (
            ("Full IPv6 address",
                '2001:DB8:0:0:0:0:0:1', (username, '2001:DB8:0:0:0:0:0:1', '22')),
            ("IPv6 address in short form",
                '2001:DB8::1', (username, '2001:DB8::1', '22')),
            ("IPv6 localhost",
                '::1', (username, '::1', '22')),
            ("Square brackets are required to separate non-standard port from IPv6 address",
                '[2001:DB8::1]:1222', (username, '2001:DB8::1', '1222')),
            ("Username and IPv6 address",
                'user@2001:DB8::1', ('user', '2001:DB8::1', '22')),
            ("Username and IPv6 address with non-standard port",
                'user@[2001:DB8::1]:1222', ('user', '2001:DB8::1', '1222')),
        ):
            eq_.description = "Host-string IPv6 normalization: %s" % description
            yield eq_, normalize(input), output_
            del eq_.description

    def test_normalization_without_port(self):
        """
        normalize() and join_host_strings() omit port if omit_port given
        """
        eq_(
            join_host_strings(*normalize('user@localhost', omit_port=True)),
            'user@localhost'
        )

    def test_ipv6_host_strings_join(self):
        """
        join_host_strings() should use square brackets only for IPv6 and if port is given
        """
        eq_(
            join_host_strings('user', '2001:DB8::1'),
            'user@2001:DB8::1'
        )
        eq_(
            join_host_strings('user', '2001:DB8::1', '1222'),
            'user@[2001:DB8::1]:1222'
        )
        eq_(
            join_host_strings('user', '192.168.0.0', '1222'),
            'user@192.168.0.0:1222'
        )

    def test_nonword_character_in_username(self):
        """
        normalize() will accept non-word characters in the username part
        """
        eq_(
            normalize('user-with-hyphens@someserver.org')[0],
            'user-with-hyphens'
        )

    def test_at_symbol_in_username(self):
        """
        normalize() should allow '@' in usernames (i.e. last '@' is split char)
        """
        parts = normalize('user@example.com@www.example.com')
        eq_(parts[0], 'user@example.com')
        eq_(parts[1], 'www.example.com')

    def test_normalization_of_empty_input(self):
        empties = ('', '', '')
        for description, input in (
            ("empty string", ''),
            ("None", None)
        ):
            template = "normalize() returns empty strings for %s input"
            eq_.description = template % description
            yield eq_, normalize(input), empties
            del eq_.description

    def test_host_string_denormalization(self):
        username = _get_system_username()
        for description, string1, string2 in (
            ("Sanity check: equal strings remain equal",
                'localhost', 'localhost'),
            ("Empty username is same as get_system_username",
                'localhost:22', username + '@localhost:22'),
            ("Empty port is same as port 22",
                'user@localhost', 'user@localhost:22'),
            ("Both username and port",
                'localhost', username + '@localhost:22'),
            ("IPv6 address",
                '2001:DB8::1', username + '@[2001:DB8::1]:22'),
        ):
            eq_.description = "Host-string denormalization: %s" % description
            yield eq_, denormalize(string1), denormalize(string2)
            del eq_.description

    #
    # Connection caching
    #
    @staticmethod
    @with_fakes
    def check_connection_calls(host_strings, num_calls):
        # Clear Fudge call stack
        # Patch connect() with Fake obj set to expect num_calls calls
        patched_connect = patch_object('fabric.network', 'connect',
            Fake('connect', expect_call=True).times_called(num_calls)
        )
        try:
            # Make new cache object
            cache = HostConnectionCache()
            # Connect to all connection strings
            for host_string in host_strings:
                # Obtain connection from cache, potentially calling connect()
                cache[host_string]
        finally:
            # Restore connect()
            patched_connect.restore()

    def test_connection_caching(self):
        for description, host_strings, num_calls in (
            ("Two different host names, two connections",
                ('localhost', 'other-system'), 2),
            ("Same host twice, one connection",
                ('localhost', 'localhost'), 1),
            ("Same host twice, different ports, two connections",
                ('localhost:22', 'localhost:222'), 2),
            ("Same host twice, different users, two connections",
                ('user1@localhost', 'user2@localhost'), 2),
        ):
            TestNetwork.check_connection_calls.description = description
            yield TestNetwork.check_connection_calls, host_strings, num_calls

    def test_connection_cache_deletion(self):
        """
        HostConnectionCache should delete correctly w/ non-full keys
        """
        hcc = HostConnectionCache()
        fake = Fake('connect', callable=True)
        with patched_context('fabric.network', 'connect', fake):
            for host_string in ('hostname', 'user@hostname',
                'user@hostname:222'):
                # Prime
                hcc[host_string]
                # Test
                ok_(host_string in hcc)
                # Delete
                del hcc[host_string]
                # Test
                ok_(host_string not in hcc)

    #
    # Connection loop flow
    #
    @server()
    def test_saved_authentication_returns_client_object(self):
        cache = HostConnectionCache()
        assert isinstance(cache[env.host_string], ssh.SSHClient)

    @server()
    @with_fakes
    def test_prompts_for_password_without_good_authentication(self):
        env.password = None
        with password_response(PASSWORDS[env.user], times_called=1):
            cache = HostConnectionCache()
            cache[env.host_string]

    @aborts
    def test_aborts_on_prompt_with_abort_on_prompt(self):
        """
        abort_on_prompt=True should abort when prompt() is used
        """
        env.abort_on_prompts = True
        prompt("This will abort")

    @server()
    @aborts
    def test_aborts_on_password_prompt_with_abort_on_prompt(self):
        """
        abort_on_prompt=True should abort when password prompts occur
        """
        env.password = None
        env.abort_on_prompts = True
        with password_response(PASSWORDS[env.user], times_called=1):
            cache = HostConnectionCache()
            cache[env.host_string]

    @with_fakes
    @raises(NetworkError)
    def test_connect_does_not_prompt_password_when_ssh_raises_channel_exception(self):
        def raise_channel_exception_once(*args, **kwargs):
            if raise_channel_exception_once.should_raise_channel_exception:
                raise_channel_exception_once.should_raise_channel_exception = False
                raise ssh.ChannelException(2, 'Connect failed')
        raise_channel_exception_once.should_raise_channel_exception = True

        def generate_fake_client():
            fake_client = Fake('SSHClient', allows_any_call=True)
            fake_client.expects('connect').calls(raise_channel_exception_once)
            return fake_client

        fake_ssh = Fake('ssh', allows_any_call=True)
        fake_ssh.expects('SSHClient').calls(generate_fake_client)

        # We need the real exceptions here to preserve the inheritence structure
        # and for except clauses because python3 is picky about that
        fake_ssh.SSHException = ssh.SSHException
        fake_ssh.ChannelException = ssh.ChannelException
        fake_ssh.BadHostKeyException = ssh.BadHostKeyException
        fake_ssh.AuthenticationException = ssh.AuthenticationException
        fake_ssh.PasswordRequiredException = ssh.PasswordRequiredException

        patched_connect = patch_object('fabric.network', 'ssh', fake_ssh)
        patched_password = patch_object('fabric.network', 'prompt_for_password',
                                        Fake('prompt_for_password', callable=True).times_called(0))
        try:
            connect('user', 'localhost', 22, HostConnectionCache())
        finally:
            # Restore ssh
            patched_connect.restore()
            patched_password.restore()

    @mock_streams('stdout')
    @server()
    def test_does_not_abort_with_password_and_host_with_abort_on_prompt(self):
        """
        abort_on_prompt=True should not abort if no prompts are needed
        """
        env.abort_on_prompts = True
        env.password = PASSWORDS[env.user]
        # env.host_string is automatically filled in when using server()
        run("ls /simple")

    @mock_streams('stdout')
    @server()
    def test_trailing_newline_line_drop(self):
        """
        Trailing newlines shouldn't cause last line to be dropped.
        """
        # Multiline output with trailing newline
        cmd = "ls /"
        output_string = RESPONSES[cmd]
        # TODO: fix below lines, duplicates inner workings of tested code
        prefix = "[%s] out: " % env.host_string
        expected = prefix + ('\n' + prefix).join(output_string.split('\n'))
        # Create, tie off thread
        with settings(show('everything'), hide('running')):
            result = run(cmd)
            # Test equivalence of expected, received output
            eq_(expected, sys.stdout.getvalue())
            # Also test that the captured value matches, too.
            eq_(output_string, result)

    @server()
    def test_sudo_prompt_kills_capturing(self):
        """
        Sudo prompts shouldn't screw up output capturing
        """
        cmd = "ls /simple"
        with hide('everything'):
            eq_(sudo(cmd), RESPONSES[cmd])

    @server()
    def test_password_memory_on_user_switch(self):
        """
        Switching users mid-session should not screw up password memory
        """
        def _to_user(user):
            return join_host_strings(user, env.host, env.port)

        user1 = 'root'
        user2 = USER
        with settings(hide('everything'), password=None):
            # Connect as user1 (thus populating both the fallback and
            # user-specific caches)
            with settings(
                password_response(PASSWORDS[user1]),
                host_string=_to_user(user1)
            ):
                run("ls /simple")
            # Connect as user2: * First cxn attempt will use fallback cache,
            # which contains user1's password, and thus fail * Second cxn
            # attempt will prompt user, and succeed due to mocked p4p * but
            # will NOT overwrite fallback cache
            with settings(
                password_response(PASSWORDS[user2]),
                host_string=_to_user(user2)
            ):
                # Just to trigger connection
                run("ls /simple")
            # * Sudo call should use cached user2 password, NOT fallback cache,
            # and thus succeed. (I.e. p_f_p should NOT be called here.)
            with settings(
                password_response('whatever', times_called=0),
                host_string=_to_user(user2)
            ):
                sudo("ls /simple")

    @mock_streams('stderr')
    @server()
    def test_password_prompt_displays_host_string(self):
        """
        Password prompt lines should include the user/host in question
        """
        env.password = None
        env.no_agent = env.no_keys = True
        with show('everything'), password_response(PASSWORDS[env.user], silent=False):
            run("ls /simple")
        regex = r"^\[%s\] Login password for '%s': " % (env.host_string, env.user)
        assert_contains(regex, sys.stderr.getvalue())

    @mock_streams('stderr')
    @server(pubkeys=True)
    def test_passphrase_prompt_displays_host_string(self):
        """
        Passphrase prompt lines should include the user/host in question
        """
        env.password = None
        env.no_agent = env.no_keys = True
        env.key_filename = CLIENT_PRIVKEY
        with hide('everything'), password_response(CLIENT_PRIVKEY_PASSPHRASE, silent=False):
            run("ls /simple")
        regex = r"^\[%s\] (Passphrase for private key: |Login password for '%s': )" % (
            env.host_string, env.user
        )
        assert_contains(regex, sys.stderr.getvalue())

    def test_sudo_prompt_display_passthrough(self):
        """
        Sudo prompt should display (via passthrough) when stdout/stderr shown
        """
        TestNetwork._prompt_display(True)

    def test_sudo_prompt_display_directly(self):
        """
        Sudo prompt should display (manually) when stdout/stderr hidden
        """
        TestNetwork._prompt_display(False)

    @staticmethod
    @mock_streams('both')
    @server(pubkeys=True, responses={'oneliner': 'result'})
    def _prompt_display(display_output):
        env.password = None
        env.no_agent = env.no_keys = True
        env.key_filename = CLIENT_PRIVKEY
        output.output = display_output
        with password_response(
            (CLIENT_PRIVKEY_PASSPHRASE, PASSWORDS[env.user]),
            silent=False
        ):
            sudo('oneliner')
        if display_output:
            expected = textwrap.dedent(r"""
                \[%(prefix)s\] sudo: oneliner(\nConnect error: .*)?
                \[%(prefix)s\] (Passphrase for private key: |Login password for '%(user)s': )
                \[%(prefix)s\] out: sudo password:
                \[%(prefix)s\] out: Sorry, try again.
                \[%(prefix)s\] out: sudo password: 
                \[%(prefix)s\] out: result
                """[1:]) % {'prefix': env.host_string, 'user': env.user}  # noqa: W291
        else:
            # Note lack of first sudo prompt (as it's autoresponded to) and of
            # course the actual result output.
            expected = textwrap.dedent(r"""
                \[%(prefix)s\] sudo: oneliner(\nConnect error: .*)?
                \[%(prefix)s\] (Passphrase for private key: |Login password for '%(user)s': )
                \[%(prefix)s\] out: Sorry, try again.
                \[%(prefix)s\] out: sudo password: 
                """[1:])[:-1] % {'prefix': env.host_string, 'user': env.user}  # noqa: W291

        match_(sys.stdall.getvalue(), expected)

    @mock_streams('both')
    @server(
        pubkeys=True,
        responses={'oneliner': 'result', 'twoliner': 'result1\nresult2'}
    )
    def test_consecutive_sudos_should_not_have_blank_line(self):
        """
        Consecutive sudo() calls should not incur a blank line in-between
        """
        env.password = None
        env.no_agent = env.no_keys = True
        env.key_filename = CLIENT_PRIVKEY
        with password_response(
            (CLIENT_PRIVKEY_PASSPHRASE, PASSWORDS[USER]),
            silent=False
        ):
            sudo('oneliner')
            sudo('twoliner')

        expected = textwrap.dedent(r"""
            \[%(prefix)s\] sudo: oneliner(\nConnect error: .*)?
            \[%(prefix)s\] (Passphrase for private key: |Login password for '%(user)s': )
            \[%(prefix)s\] out: sudo password:
            \[%(prefix)s\] out: Sorry, try again.
            \[%(prefix)s\] out: sudo password: 
            \[%(prefix)s\] out: result
            \[%(prefix)s\] sudo: twoliner
            \[%(prefix)s\] out: sudo password:
            \[%(prefix)s\] out: result1
            \[%(prefix)s\] out: result2
            """[1:]) % {'prefix': env.host_string, 'user': env.user}  # noqa: W291
        match_(sys.stdall.getvalue(), expected)

    @mock_streams('both')
    @server(pubkeys=True, responses={'silent': '', 'normal': 'foo'})
    def test_silent_commands_should_not_have_blank_line(self):
        """
        Silent commands should not generate an extra trailing blank line

        After the move to interactive I/O, it was noticed that while run/sudo
        commands which had non-empty stdout worked normally (consecutive such
        commands were totally adjacent), those with no stdout (i.e. silent
        commands like ``test`` or ``mkdir``) resulted in spurious blank lines
        after the "run:" line. This looks quite ugly in real world scripts.
        """
        env.password = None
        env.no_agent = env.no_keys = True
        env.key_filename = CLIENT_PRIVKEY
        with password_response(CLIENT_PRIVKEY_PASSPHRASE, silent=False):
            run('normal')
            run('silent')
            run('normal')
            with hide('everything'):
                run('normal')
                run('silent')
        expected = textwrap.dedent(r"""
            \[%(prefix)s\] run: normal(\nConnect error: .*)?
            \[%(prefix)s\] (Passphrase for private key: |Login password for '%(user)s': )
            \[%(prefix)s\] out: foo
            \[%(prefix)s\] run: silent
            \[%(prefix)s\] run: normal
            \[%(prefix)s\] out: foo
            """[1:]) % {'prefix': env.host_string, 'user': env.user}
        match_(sys.stdall.getvalue(), expected)

    @mock_streams('both')
    @server(
        pubkeys=True,
        responses={'oneliner': 'result', 'twoliner': 'result1\nresult2'}
    )
    def test_io_should_print_prefix_if_ouput_prefix_is_true(self):
        """
        run/sudo should print [host_string] if env.output_prefix == True
        """
        env.password = None
        env.no_agent = env.no_keys = True
        env.key_filename = CLIENT_PRIVKEY
        with password_response(
            (CLIENT_PRIVKEY_PASSPHRASE, PASSWORDS[USER]),
            silent=False
        ):
            run('oneliner')
            run('twoliner')
        expected = textwrap.dedent(r"""
            \[%(prefix)s\] run: oneliner(\nConnect error: .*)?
            \[%(prefix)s\] (Passphrase for private key: |Login password for '%(user)s': )
            \[%(prefix)s\] out: result
            \[%(prefix)s\] run: twoliner
            \[%(prefix)s\] out: result1
            \[%(prefix)s\] out: result2
            """[1:]) % {'prefix': env.host_string, 'user': env.user}
        match_(sys.stdall.getvalue(), expected)

    @mock_streams('both')
    @server(
        pubkeys=True,
        responses={'oneliner': 'result', 'twoliner': 'result1\nresult2'}
    )
    def test_io_should_not_print_prefix_if_ouput_prefix_is_false(self):
        """
        run/sudo shouldn't print [host_string] if env.output_prefix == False
        """
        env.password = None
        env.no_agent = env.no_keys = True
        env.key_filename = CLIENT_PRIVKEY
        with password_response(
            (CLIENT_PRIVKEY_PASSPHRASE, PASSWORDS[USER]),
            silent=False
        ):
            with settings(output_prefix=False):
                run('oneliner')
                run('twoliner')
        expected = textwrap.dedent(r"""
            \[%(prefix)s\] run: oneliner(\nConnect error: .*)?
            \[%(prefix)s\] (Passphrase for private key: |Login password for '%(user)s': )
            result
            \[%(prefix)s\] run: twoliner
            result1
            result2
            """[1:]) % {'prefix': env.host_string, 'user': env.user}
        match_(sys.stdall.getvalue(), expected)

    @server()
    def test_env_host_set_when_host_prompt_used(self):
        """
        Ensure env.host is set during host prompting
        """
        copied_host_string = str(env.host_string)
        fake = Fake('input', callable=True).returns(copied_host_string)
        env.host_string = None
        env.host = None
        with settings(hide('everything'), patched_input(fake)):
            run("ls /")
        # Ensure it did set host_string back to old value
        eq_(env.host_string, copied_host_string)
        # Ensure env.host is correct
        eq_(env.host, normalize(copied_host_string)[1])


def subtask():
    run("This should never execute")

class TestConnections(FabricTest):
    @aborts
    def test_should_abort_when_cannot_connect(self):
        """
        By default, connecting to a nonexistent server should abort.
        """
        with hide('everything'):
            execute(subtask, hosts=['nope.nonexistent.com'])

    def test_should_warn_when_skip_bad_hosts_is_True(self):
        """
        env.skip_bad_hosts = True => execute() skips current host
        """
        with settings(hide('everything'), skip_bad_hosts=True):
            execute(subtask, hosts=['nope.nonexistent.com'])

    @server()
    def test_host_not_in_known_hosts_exception(self):
        """
        Check reject_unknown_hosts exception
        """
        with settings(
            hide('everything'), password=None, reject_unknown_hosts=True,
            disable_known_hosts=True, abort_on_prompts=True,
        ):
            try:
                run("echo foo")
            except NetworkError as exc:
                exp = "Server '[127.0.0.1]:2200' not found in known_hosts"
                assert str(exc) == exp, "%s != %s" % (exc, exp)
            else:
                raise AssertionError("Host connected without valid "
                                     "fingerprint.")


@parallel
def parallel_subtask():
    run("This should never execute")

class TestParallelConnections(FabricTest):
    @aborts
    def test_should_abort_when_cannot_connect(self):
        """
        By default, connecting to a nonexistent server should abort.
        """
        with hide('everything'):
            execute(parallel_subtask, hosts=['nope.nonexistent.com'])

    def test_should_warn_when_skip_bad_hosts_is_True(self):
        """
        env.skip_bad_hosts = True => execute() skips current host
        """
        with settings(hide('everything'), skip_bad_hosts=True):
            execute(parallel_subtask, hosts=['nope.nonexistent.com'])


class TestSSHConfig(FabricTest):
    def env_setup(self):
        super(TestSSHConfig, self).env_setup()
        env.use_ssh_config = True
        env.ssh_config_path = support("ssh_config")
        # Undo the changes FabricTest makes to env for server support
        env.user = env.local_user
        env.port = env.default_port

    def test_global_user_with_default_env(self):
        """
        Global User should override default env.user
        """
        eq_(normalize("localhost")[0], "satan")

    def test_global_user_with_nondefault_env(self):
        """
        Global User should NOT override nondefault env.user
        """
        with settings(user="foo"):
            eq_(normalize("localhost")[0], "foo")

    def test_specific_user_with_default_env(self):
        """
        Host-specific User should override default env.user
        """
        eq_(normalize("myhost")[0], "neighbor")

    def test_user_vs_host_string_value(self):
        """
        SSH-config derived user should NOT override host-string user value
        """
        eq_(normalize("myuser@localhost")[0], "myuser")
        eq_(normalize("myuser@myhost")[0], "myuser")

    def test_global_port_with_default_env(self):
        """
        Global Port should override default env.port
        """
        eq_(normalize("localhost")[2], "666")

    def test_global_port_with_nondefault_env(self):
        """
        Global Port should NOT override nondefault env.port
        """
        with settings(port="777", use_ssh_config=False):
            eq_(normalize("localhost")[2], "777")

    def test_specific_port_with_default_env(self):
        """
        Host-specific Port should override default env.port
        """
        eq_(normalize("myhost")[2], "664")

    def test_port_vs_host_string_value(self):
        """
        SSH-config derived port should NOT override host-string port value
        """
        eq_(normalize("localhost:123")[2], "123")
        eq_(normalize("myhost:123")[2], "123")

    def test_hostname_alias(self):
        """
        Hostname setting overrides host string's host value
        """
        eq_(normalize("localhost")[1], "localhost")
        eq_(normalize("myalias")[1], "otherhost")

    @with_patched_object('fabric.utils', 'warn',
                         Fake('warn', callable=True, expect_call=True))
    def test_warns_with_bad_config_file_path(self):
        # use_ssh_config is already set in our env_setup()
        with settings(hide('everything'), ssh_config_path="nope_bad_lol"):
            normalize('foo')

    @server()
    def test_real_connection(self):
        """
        Test-server connection using ssh_config values
        """
        with settings(
            hide('everything'),
            ssh_config_path=support("testserver_ssh_config"),
            host_string='testserver',
        ):
            ok_(run("ls /simple").succeeded)


class TestKeyFilenames(FabricTest):
    def test_empty_everything(self):
        """
        No env.key_filename and no ssh_config = empty list
        """
        with settings(use_ssh_config=False):
            with settings(key_filename=""):
                eq_(key_filenames(), [])
            with settings(key_filename=[]):
                eq_(key_filenames(), [])

    def test_just_env(self):
        """
        Valid env.key_filename and no ssh_config = just env
        """
        with settings(use_ssh_config=False):
            with settings(key_filename="mykey"):
                eq_(key_filenames(), ["mykey"])
            with settings(key_filename=["foo", "bar"]):
                eq_(key_filenames(), ["foo", "bar"])

    def test_just_ssh_config(self):
        """
        No env.key_filename + valid ssh_config = ssh value
        """
        with settings(use_ssh_config=True, ssh_config_path=support("ssh_config")):
            for val in ["", []]:
                with settings(key_filename=val):
                    eq_(key_filenames(), ["foobar.pub"])

    def test_both(self):
        """
        Both env.key_filename + valid ssh_config = both show up w/ env var first
        """
        with settings(use_ssh_config=True, ssh_config_path=support("ssh_config")):
            with settings(key_filename="bizbaz.pub"):
                eq_(key_filenames(), ["bizbaz.pub", "foobar.pub"])
            with settings(key_filename=["bizbaz.pub", "whatever.pub"]):
                expected = ["bizbaz.pub", "whatever.pub", "foobar.pub"]
                eq_(key_filenames(), expected)
