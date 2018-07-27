"""
HTTP Client is used make a request.
"""
from abc import ABC, abstractmethod

__all__ = ['HttpClient']


class HttpClient(ABC):
    """
    The abstract class defined the behavior of HTTP client, that is making an HTTP request.
    """

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    @abstractmethod
    def request(self, method, url, *args, **kwargs):
        """HTTP request"""
        raise NotImplementedError

    @abstractmethod
    def get(self, url, *args, **kwargs):
        """HTTP GET request"""
        raise NotImplementedError

    @abstractmethod
    def post(self, url, *args, data=None, **kwargs):
        """HTTP POST request"""
        raise NotImplementedError

    @abstractmethod
    def put(self, url, *args, data=None, **kwargs):
        """HTTP PUT request"""
        raise NotImplementedError

    @abstractmethod
    def delete(self, url, *args, **kwargs):
        """HTTP DELETE request"""
        raise NotImplementedError

    @abstractmethod
    def options(self, url, *args, **kwargs):
        """HTTP OPTIONS request"""
        raise NotImplementedError

    @abstractmethod
    def head(self, url, *args, **kwargs):
        """HTTP HEAD request"""
        raise NotImplementedError

    @abstractmethod
    def patch(self, url, *args, data=None, **kwargs):
        """HTTP PATCH request"""
        raise NotImplementedError

    @abstractmethod
    def close(self):
        """Release all acquired resources"""
        raise NotImplementedError

    @abstractmethod
    def get_response(self, response):
        """
        Return an object (common_crawler.http.Response) based on the response from the HTTP client.
        """
        raise NotImplementedError

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
