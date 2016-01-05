.. image:: https://travis-ci.org/ImmobilienScout24/succubus.svg
    :alt: Travis build status image
    :align: left
    :target: https://travis-ci.org/ImmobilienScout24/succubus

.. image:: https://coveralls.io/repos/ImmobilienScout24/succubus/badge.svg?branch=master
  :alt: Coverage status
  :target: https://coveralls.io/github/ImmobilienScout24/succubus?branch=master


========
succubus
========

Description
===========
succubus is a lightweight python module for a fast and easy creation of
python daemons.

Examples
========

.. code-block:: python

    import logging
    import sys

    from logging.handlers import WatchedFileHandler

    from succubus import Daemon


    class MyDaemon(Daemon):
        def __init__(self, *args, **kwargs):
            super(MyDaemon, self).__init__(*args, **kwargs)

        def run(self):
            """Overwrite the run function of the daemon class"""
            handler = WatchedFileHandler('succubus.log')
            self.logger = logging.getLogger('succubus')
            self.logger.addHandler(handler)
            while True:
                time.sleep(1)
                self.logger.warn('Hello world')


    def main():
        daemon = MyDaemon(pid_file='succubus.pid')
        sys.exit(daemon.action())


    if __name__ == '__main__':
        main()
