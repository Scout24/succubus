from __future__ import print_function, absolute_import, division

from unittest2 import TestCase
from mock import patch

from succubus import Daemon



class TestDaemonize(TestCase):
    @patch('succubus.daemonize.sys')
    def test_must_pop_sys_argv_before_loading_config(self, mock_sys):
        """The sys.argv.pop() must happen before load_configuration()

        This way, load_configuration() has a chance to parse the command
        line arguments, which may contain something like a --config=xyz
        parameter that affects config loading.
        """
        class MyDaemon(Daemon):
            def load_configuration(self):
                if self.param1 != 'start':
                    raise Exception("param1 not yet set")

        mock_sys.argv = ['foo', 'start', '--config=xyz']

        a = MyDaemon(pid_file='foo.pid')

    @patch("succubus.daemonize.os.setgid")
    def test_set_gid_translates_group_name(self, mock_setgid):
        daemon = Daemon(pid_file="foo")
        daemon.group = "root"

        daemon.set_gid()

        mock_setgid.assert_called_with(0)

    @patch("succubus.daemonize.os.setuid")
    def test_set_uid_translates_user_name(self, mock_setuid):
        daemon = Daemon(pid_file="foo")
        daemon.user = "root"

        daemon.set_uid()

        mock_setuid.assert_called_with(0)
