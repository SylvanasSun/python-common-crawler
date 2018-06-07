"""
The module pipeline is for transmitting parsed data from HTTP response,
a destination of transmission can be file or database.
"""

from abc import ABC, abstractmethod

from common_crawler.crawler import FetchedUrl

__all__ = ['Pipeline']


class Pipeline(ABC):
    """
    The class Pipeline represents receive a class FetchedUrl from Engine then
    transmit parsed data, the user can get some information from self.task (FetchedUrl)
    and determine transfer behavior by means of function handle(), setup() and close()
    """

    def __init__(self, task, **kwargs):
        if not isinstance(task, FetchedUrl):
            raise ValueError('Received class of the param task must be %s, currently got %s'
                             % ('FetchedUrl', task.__class__.__name__))

        self.data = task.parsed_data
        self.task = task
        self.__dict__.update(kwargs)

    def transmit(self):
        """
        function transmit() will be called by Engine and user don't need to implement it
        """
        try:
            self.setup()
            self.handle()
        finally:
            self.close()

    @abstractmethod
    def setup(self, **kwargs):
        """some pre-operation of transmitting"""
        raise NotImplementedError

    @abstractmethod
    def handle(self, **kwargs):
        """handle how to transmit data"""
        raise NotImplementedError

    @abstractmethod
    def close(self, **kwargs):
        """some post-operation of transmitting"""
        raise NotImplementedError

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
