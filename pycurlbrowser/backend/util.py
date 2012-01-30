# coding: utf-8

from datetime import datetime

class StopWatch(object):

    """
    A class for use in timing blocks, via "with" keyword functionality.
    """

    def __init__(self):
        self._start = None
        self.total = None

    def __enter__(self):
        self._start = datetime.now()
        return self

    def __exit__(self, typ, value, traceback):
        self.total = datetime.now() - self._start
