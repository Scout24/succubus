#!/usr/bin/env python
from __future__ import print_function, absolute_import, division

import os
import psutil
import shutil
import subprocess
import tempfile
import time
import unittest2

class ShutdownTimeoutTests(unittest2.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="succubus-test")
        self.pid_file = os.path.join(self.temp_dir, 'succubus.pid')
        os.environ['PID_FILE'] = self.pid_file

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_reliable_kill(self):
        """reliable_kill must send SIGKILL after the configured timeout"""
        daemon = "./src/integrationtest/python/shutdown_timeout_daemon.py"
        subprocess.check_call([daemon, "start"])

        time.sleep(0.3)
        subprocess.check_call([daemon, "status"])
        with open(self.pid_file) as pid_file:
            daemon_pid = int(pid_file.read().strip())
        self.assertTrue(psutil.pid_exists(daemon_pid))

        start = time.time()
        subprocess.check_call([daemon, "stop"])
        stop = time.time()

        shutdown_time = stop - start
        # reliable_kill() must give the process 1.4 seconds to shut down...
        self.assertGreater(shutdown_time, 1.4)
        # ...but not much more than that.
        self.assertLess(shutdown_time, 1.7)

        # Daemon must be stopped from init script point of view.
        self.assertRaises(Exception, subprocess.check_call, [daemon, "status"])
        # And the process must really be gone.
        self.assertFalse(psutil.pid_exists(daemon_pid))


if __name__ == "__main__":
    unittest2.main()
