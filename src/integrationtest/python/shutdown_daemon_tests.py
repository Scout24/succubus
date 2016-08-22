#!/usr/bin/env python
from __future__ import print_function, absolute_import, division

import os
import shutil
import subprocess
import tempfile
import time
import unittest2

class ShutdownDaemonTests(unittest2.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="succubus-test")
        self.pid_file = os.path.join(self.temp_dir, 'succubus.pid')
        os.environ['PID_FILE'] = self.pid_file

    def tearDown(self):
        #shutil.rmtree(self.temp_dir)
        print(self.temp_dir)

    def test_daemon_start_status_stop(self):
        daemon = "./src/integrationtest/python/shutdown_daemon.py"
        subprocess.check_call([daemon, "start"])

        time.sleep(0.3)
        subprocess.check_call([daemon, "status"])
        subprocess.check_call([daemon, "stop"])

        success_file = os.path.join(self.temp_dir, "success")
        self.assertTrue(os.path.exists(success_file))


if __name__ == "__main__":
    unittest2.main()
