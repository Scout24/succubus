#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import, division

from logging.handlers import SysLogHandler
import logging
import os
import signal
import sys
import time
import atexit
import psutil

from pwd import getpwnam
from grp import getgrnam
from signal import SIGTERM, SIGKILL


class Daemon(object):
    """Subclass this Daemon class and override the run() method"""

    def __init__(self,
                 pid_file=None,
                 stdin='/dev/null',
                 stdout='/dev/null',
                 stderr='/dev/null'):
        if len(sys.argv) == 1:
            self.param1 = None
            return
        self.param1 = sys.argv.pop(1)

        self.stdin = os.path.abspath(stdin)
        self.stdout = os.path.abspath(stdout)
        self.stderr = os.path.abspath(stderr)
        self.config = {}
        self.load_configuration()
        self.user = self.config.get('user')
        self.group = self.config.get('group')
        if not pid_file:
            raise Exception("You did not provide a pid file")
        self.pid_file = os.path.abspath(pid_file)
        self.pid = None
        self.shutdown_timeout = 10

    def set_gid(self):
        """Change the group of the running process"""
        if self.group:
            gid = getgrnam(self.group).gr_gid
            try:
                os.setgid(gid)
            except Exception:
                message = ("Unable to switch ownership to {0}:{1}. " +
                           "Did you start the daemon as root?")
                print(message.format(self.user, self.group))
                sys.exit(1)

    def set_uid(self):
        """Change the user of the running process"""
        if self.user:
            uid = getpwnam(self.user).pw_uid
            try:
                os.setuid(uid)
            except Exception:
                message = ('Unable to switch ownership to {0}:{1}. ' +
                           'Did you start the daemon as root?')
                print(message.format(self.user, self.group))
                sys.exit(1)

    @staticmethod
    def usage():
        sys.stdout.write("Usage: %s {start|stop|restart|status}\n" % sys.argv[0])
        return 2

    def action(self):
        if self.param1 == 'start':
            return self.start()
        elif self.param1 == 'stop':
            return self.stop()
        elif self.param1 == 'restart':
            return self.restart()
        elif self.param1 == 'status':
            return self.status()
        else:
            return self.usage()

    def load_configuration(self):
        """Set up self.config if needed"""
        pass

    def setup_logging(self):
        """Set up self.logger

        This function is called after load_configuration() and after changing
        to new user/group IDs (if configured). Logging to syslog using the
        root logger is configured by default, you can override this method if
        you want something else.
        """
        self.logger = logging.getLogger()

        if os.path.exists('/dev/log'):
            handler = SysLogHandler('/dev/log')
        else:
            handler = SysLogHandler()
        self.logger.addHandler(handler)

    def shutdown(self):
        """Clean up when daemon is about to terminate

        This function allows your daemon to perform cleanup work just before
        terminating. It is called no matter why the daemon terminates (calling
        "stop" on the init script, self.run() raising an exception....).
        """
        pass

    def _shutdown(self):
        try:
            self.shutdown()
        except Exception:
            self.logger.exception("Error in daemon shutdown:")
        self.delpid()

    def daemonize(self):
        """
        Do the UNIX double-fork magic, see Stevens' "Advanced
        Programming in the UNIX Environment" for details (ISBN 0201563177)
        http://www.erlenstar.demon.co.uk/unix/faq_2.html#SEC16
        """
        try:
            pid = os.fork()
            if pid > 0:
                sys.exit(0)
        except OSError as e:
            sys.stderr.write('fork #1 failed: %d (%s)\n' %
                             (e.errno, e.strerror))
            sys.exit(1)
        os.chdir('/')
        os.setsid()
        os.umask(0)
        try:
            pid = os.fork()
            if pid > 0:
                sys.exit(0)
        except OSError as e:
            sys.stderr.write('fork #2 failed: %d (%s)\n' %
                             (e.errno, e.strerror))
            sys.exit(1)
        # to properly close the fd's, we need to use sys and os:
        # http://chromano.me/2011/05/23/starting-python-daemons-via-ssh.html
        sys.stdin.close()
        os.close(0)
        sys.stdout.close()
        os.close(1)
        sys.stderr.close()
        os.close(2)

        pid = os.getpid()
        open(self.pid_file, 'w+').write("%s\n" % pid)

        def handler(*args):
            raise BaseException("SIGTERM was caught")
        signal.signal(signal.SIGTERM, handler)
        # atexit functions are "not called when the program is killed by a
        # signal not handled by Python". But since SIGTERM is now handled, the
        # atexit functions do get called.
        atexit.register(self._shutdown)

    def delpid(self):
        """Remove the pid_file from filesystem"""
        os.remove(self.pid_file)

    def _already_running(self):
        try:
            self.pid = int(open(self.pid_file).read().strip())
        except IOError:
            self.pid = None
            return False
        if psutil.pid_exists(self.pid):
            return True
        return False

    def start(self):
        """Start the daemon"""
        if self._already_running():
            message = 'pid file %s already exists. Daemon already running?\n'
            sys.stderr.write(message % self.pid_file)
            return 0
        self.set_gid()
        self.set_uid()
        # Create log files (if configured) with the new user/group. Creating
        # them as root would allow symlink exploits.
        self.setup_logging()
        # Create pid file with new user/group. This ensures we will be able
        # to delete the file when shutting down.
        self.daemonize()
        try:
            self.run()
        except Exception:
            self.logger.exception('Exception while running the daemon:')
            return 1
        return 0

    def reliable_kill(self):
        try:
            os.kill(self.pid, SIGTERM)
            for _ in range(int(self.shutdown_timeout * 10)):
                os.kill(self.pid, 0)
                time.sleep(0.1)
        except OSError as err:
            err = str(err)
            if 'No such process' in err:
                if os.path.exists(self.pid_file):
                    self.delpid()
                return 0
            else:
                print(err)
                return 1

        # No 'no such process' exception -> process is still running.
        sys.stderr.write('Had to kill the process with SIGKILL')
        os.kill(self.pid, SIGKILL)
        return 0

    def stop(self):
        """Stop the daemon"""
        if self._already_running():
            return self.reliable_kill()
        else:
            # FIXME: misleading error message
            message = 'Daemon not running, nothing to do.\n'
            sys.stderr.write(message)
            return 0

    def restart(self):
        """Restart the daemon"""
        self.stop()
        self.start()

    def run(self):
        """Placeholder for later overwriting"""
        raise NotImplementedError

    def status(self):
        """Determine the status of the daemon"""
        my_name = os.path.basename(sys.argv[0])
        if self._already_running():
            message = "{0} (pid  {1}) is running...\n".format(my_name, self.pid)
            sys.stdout.write(message)
            return 0
        sys.stdout.write("{0} is stopped\n".format(my_name))
        return 3
