#!/usr/bin/env python
from __future__ import print_function, absolute_import, division

import os
import shutil
import subprocess
import tempfile
import time
import unittest2

class BasicDaemonTests(unittest2.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="succubus-test")
        self.pid_file = os.path.join(self.temp_dir, 'succubus.pid')
        os.environ['PID_FILE'] = self.pid_file

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_daemon_start_status_stop(self):
        daemon = "./src/integrationtest/python/basic_daemon.py"
        subprocess.check_call([daemon, "start"])

        time.sleep(0.3)
        # Daemon must be running, PID file created.
        subprocess.check_call([daemon, "status"])
        self.assertTrue(os.path.exists(self.pid_file))
        # Calling "start" again should not do anything.
        subprocess.check_call([daemon, "start"])

        subprocess.check_call([daemon, "stop"])

        # Daemon must be stopped as soon as "stop" returns.
        self.assertRaises(Exception, subprocess.check_call, [daemon, "status"])
        # Daemon must remove its PID file on clean shutdown.
        self.assertFalse(os.path.exists(self.pid_file))
        # Calling "stop" again should not do anything.
        subprocess.check_call([daemon, "stop"])


if __name__ == "__main__":
    unittest2.main()
