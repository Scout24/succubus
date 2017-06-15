#!/usr/bin/env python
from __future__ import print_function, absolute_import, division

import os
import shutil
import subprocess
import tempfile
import time
import unittest2

class LoggingDaemonTests(unittest2.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="succubus-test")
        self.pid_file = os.path.join(self.temp_dir, 'succubus.pid')
        os.environ['PID_FILE'] = self.pid_file

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_daemon_start_status_stop(self):
        daemon = "./src/integrationtest/python/logging_daemon.py"
        subprocess.check_call([daemon, "start"])

        time.sleep(0.3)
        # Daemon must be running.
        subprocess.check_call([daemon, "status"])
        subprocess.check_call([daemon, "stop"])

        # Daemon must be stopped as soon as "stop" returns.
        self.assertRaises(Exception, subprocess.check_call, [daemon, "status"])


if __name__ == "__main__":
    unittest2.main()
