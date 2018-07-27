"""
The module pipeline is for transmitting parsed data from HTTP response,
a destination of transmission can be file or database.
"""

from abc import ABC, abstractmethod

from common_crawler.task import Task

__all__ = ['Pipeline']


class Pipeline(ABC):
    """
    The class Pipeline represents receive a class FetchedUrl from Engine then
    transmit parsed data, the user can get some information from self.task (FetchedUrl)
    and determine transfer behavior by means of function handle(), setup() and close()
    """

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def transmit(self, task, **kwargs):
        """
        function transmit() will be called by Engine and user don't need to implement it
        """
        self._init_task(task)

        try:
            self.setup(**kwargs)
            self.handle(**kwargs)
        finally:
            self.close(**kwargs)

    def _init_task(self, task):
        if not isinstance(task, Task):
            raise ValueError('Received class of the param task must be %s.%s, currently got %s.%s'
                             % (Task.__module__,
                                Task.__name__,
                                task.__class__.__module__,
                                task.__class__.__name__)
                             )

        self.task = task
        self.data = task.parsed_data

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
