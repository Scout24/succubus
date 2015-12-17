from unittest2 import TestCase

from succubus import Daemon

class TestDaemonize(TestCase):
    def test_one(self):
        a = Daemon(pidfile='foo')
