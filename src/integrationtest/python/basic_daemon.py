#!/usr/bin/env python
"""A daemon that does nothing for 2 seconds, then quits"""
from __future__ import print_function, absolute_import, division

import os
import sys
import time

from succubus import Daemon


class MyDaemon(Daemon):
    def run(self):
        time.sleep(2)


def main():
    daemon = MyDaemon(pid_file=os.environ['PID_FILE'])
    sys.exit(daemon.action())


if __name__ == '__main__':
    main()
