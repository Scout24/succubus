#!/usr/bin/env python
"""A daemon that has a shutdown() hook that takes a while"""
from __future__ import print_function, absolute_import, division

import logging
import os
import sys
import time

from succubus import Daemon


class MyDaemon(Daemon):
    def run(self):
        logger = logging.getLogger()
        logger.setLevel("DEBUG")
        log_dir = os.path.dirname(self.pid_file)
        log_file = os.path.join(log_dir, "daemon.log")

        logger.addHandler(logging.FileHandler(log_file))
        while True:
            logger.debug("sleeping for 1 second...")
            time.sleep(1)

    def shutdown(self):
        logger = logging.getLogger()
        logger.debug("running self.shutdown()")
        # Pretend to do something that takes a while.
        time.sleep(1.1)

        logger.debug("self.shutdown() has completed the sleep()")
        # Proof that this function completed successfully
        pid_dir = os.path.dirname(self.pid_file)
        success_file = os.path.join(pid_dir, "success")
        open(success_file, "w").close()
        logger.debug("self.shutdown() is finished")


def main():
    daemon = MyDaemon(pid_file=os.environ['PID_FILE'])
    sys.exit(daemon.action())


if __name__ == '__main__':
    main()
