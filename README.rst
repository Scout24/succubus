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
        daemon.action()


    if __name__ == '__main__':
        main()
