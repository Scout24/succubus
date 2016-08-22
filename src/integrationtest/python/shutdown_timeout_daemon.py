#!/usr/bin/env python
"""A daemon that pretends to get stuck during shutdown()

The daemon also configures self.shutdown_timeout, which must be observed
by the init script functionality.
"""
from __future__ import print_function, absolute_import, division

import logging
import os
import sys
import time

from succubus import Daemon


class MyDaemon(Daemon):
    def run(self):
        while True:
            time.sleep(1)

    def shutdown(self):
        # Pretend that the daemon is stuck and will not shut down.
        while True:
            time.sleep(1)


def main():
    daemon = MyDaemon(pid_file=os.environ['PID_FILE'])

    # Test that fractional seconds also work.
    daemon.shutdown_timeout = 1.4

    sys.exit(daemon.action())


if __name__ == '__main__':
    main()
