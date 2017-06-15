#!/usr/bin/env python
"""A daemon that relies on self.logger to be usable"""
from __future__ import print_function, absolute_import, division

import os
import sys
import time

from succubus import Daemon


class MyDaemon(Daemon):
    def run(self):
        while True:
            self.logger.error("succubus test running")
            time.sleep(1)


def main():
    daemon = MyDaemon(pid_file=os.environ['PID_FILE'])
    sys.exit(daemon.action())


if __name__ == '__main__':
    main()
