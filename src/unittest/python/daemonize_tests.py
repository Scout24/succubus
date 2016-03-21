from __future__ import print_function, absolute_import, division

from unittest2 import TestCase
from mock import patch, call
import os
import signal
import subprocess
import tempfile

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

        MyDaemon(pid_file='foo.pid')

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

    @patch("succubus.daemonize.sys")
    def test_daemon_insists_on_pidfile(self, mock_sys):
        mock_sys.argv = ['foo', 'bar']
        self.assertRaisesRegexp(Exception, "You did not provide a pid file",
                                Daemon)

    @patch("succubus.daemonize.sys")
    def test_daemon_remembers_abspath_of_pidfile(self, mock_sys):
        mock_sys.argv = ['foo', 'bar']
        daemon = Daemon(pid_file="foo")
        self.assertTrue(os.path.isabs(daemon.pid_file))

    @patch("succubus.daemonize.sys")
    def test_delpid_really_deletes_pidfile(self, mock_sys):
        mock_sys.argv = ['foo', 'bar']

        fake_pidfile = tempfile.NamedTemporaryFile()
        try:
            daemon = Daemon(pid_file=fake_pidfile.name)
            daemon.delpid()
            self.assertFalse(os.path.exists(fake_pidfile.name))
        finally:
            if os.path.exists(fake_pidfile.name):
                os.unlink(fake_pidfile.name)

    @patch("succubus.daemonize.sys")
    def test_already_running_detects_running_process(self, mock_sys):
        mock_sys.argv = ['foo', 'bar']

        fake_pidfile = tempfile.NamedTemporaryFile()
        try:
            fake_pidfile.write("{pid}\n".format(pid=os.getpid()))
            fake_pidfile.flush()

            daemon = Daemon(pid_file=fake_pidfile.name)
            self.assertEqual(daemon._already_running(), True)
            # _already_running must set the self.pid.
            self.assertEqual(daemon.pid, os.getpid())
        finally:
            os.unlink(fake_pidfile.name)

    @patch("succubus.daemonize.sys")
    def test_already_running_handles_missing_pidfile(self, mock_sys):
        mock_sys.argv = ['foo', 'bar']

        daemon = Daemon(pid_file="/a_nonexisting_pidfile")
        self.assertEqual(daemon._already_running(), False)

    @patch("succubus.daemonize.sys")
    def test_already_running_handles_missing_process(self, mock_sys):
        mock_sys.argv = ['foo', 'bar']

        # The test assumes that the OS will not reuse test_pid before
        # this function is finished.
        test_process = subprocess.Popen(['true'])
        test_pid = test_process.pid
        test_process.wait()

        fake_pidfile = tempfile.NamedTemporaryFile()
        try:
            fake_pidfile.write("{pid}\n".format(pid=test_pid))
            fake_pidfile.flush()

            daemon = Daemon(pid_file=fake_pidfile.name)
            self.assertEqual(daemon._already_running(), False)
        finally:
            os.unlink(fake_pidfile.name)

    @patch("succubus.daemonize.time.sleep")
    @patch("succubus.daemonize.os.kill")
    @patch("succubus.daemonize.sys")
    def test_reliable_kill_actually_kills(self, mock_sys, mock_kill, mock_sleep):
        mock_sys.argv = ['foo', 'bar']
        daemon = Daemon(pid_file="foo")
        daemon.pid = 1234

        # Pretend the second os.kill() fails because the process terminated.
        mock_kill.side_effect = [None, OSError("No such process")]

        retval = daemon.reliable_kill()

        self.assertEqual(retval, 0)
        self.assertEqual(mock_kill.call_count, 2)
        self.assertEqual(mock_sleep.call_count, 1)
        expected_call = call(1234, signal.SIGTERM)
        mock_kill.assert_has_calls([expected_call, expected_call])

    @patch("succubus.daemonize.time.sleep")
    @patch("succubus.daemonize.os.kill")
    @patch("succubus.daemonize.sys")
    def test_reliable_kill_kills_stuck_processes(self, mock_sys, mock_kill, mock_sleep):
        """When a process ignores SIGTERM, it must be killed with SIGKILL"""
        mock_sys.argv = ['foo', 'bar']
        daemon = Daemon(pid_file="foo")
        daemon.pid = 1234

        mock_kill.side_effect = None

        retval = daemon.reliable_kill()

        self.assertEqual(retval, 0)
        # Must have tried 100 times with SIGTERM and 1 time with SIGKILL.
        self.assertEqual(mock_kill.call_count, 101)
        mock_kill.assert_any_call(1234, signal.SIGKILL)
