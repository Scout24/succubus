#!/usr/bin/env python
"""A daemon that has a shutdown() hook that takes a while"""
from __future__ import print_function, absolute_import, division

import os
import sys
import time

from succubus import Daemon


class MyDaemon(Daemon):
    def run(self):
        while True:
            time.sleep(1)

    def shutdown(self):
        # Proof that this function completed successfully
        pid_dir = os.path.dirname(self.pid_file)
        success_file = os.path.join(pid_dir, "success")
        open(success_file, "w").close()


def main():
    daemon = MyDaemon(pid_file=os.environ['PID_FILE'])
    sys.exit(daemon.action())


if __name__ == '__main__':
    main()
