"""The crawler implements the crawling logic"""
import logging
from abc import ABC, abstractmethod

from common_crawler.configuration import CONFIGURATION
from common_crawler.utils.misc import get_function_by_name, arg_to_iter
from common_crawler.utils.url import revise_urls

__all__ = ['Crawler']

# Default global configuration
DEFAULT_NAME = CONFIGURATION.get('name', 'common_crawler')
DEFAULT_ROOTS = CONFIGURATION.get('roots', ())
DEFAULT_STRICT = CONFIGURATION.get('strict', True)
DEFAULT_MAX_REDIRECT = CONFIGURATION.get('max_redirect', 10)
DEFAULT_MAX_RETRIES = CONFIGURATION.get('max_retries', 4)


class Crawler(ABC):
    """
    The class Crawler defines a behavior that fetches a link from task queue then parse.

    A Crawler will be first to initialize the task queue base on the roots, in other words,
    push each item in the roots into the task queue and incoming parameter of the function
    add_to_task_queue(url) needs to be wrapped because the acceptable object of task queue
    is the class Task.

    There are several important data structures that are task queue, seen_urls, and finished_urls,
    the task queue be responsible for to store the object Task and each element represent a
    crawled URL then component Engine will be extract other links from the Task by LinkExtractor
    and push into the task queue, thus Crawler can get a new URL continually from the task queue to crawl,
    each crawled URL must be put in the seen_urls for distinguishing what is a duplicate, for the finished
    tasks, whether succeeded or failed, will be put in the finished_urls for subsequent recording.
    """

    def __init__(self,
                 name=DEFAULT_NAME,
                 roots=DEFAULT_ROOTS,
                 strict=DEFAULT_STRICT,
                 max_redirect=DEFAULT_MAX_REDIRECT,
                 max_retries=DEFAULT_MAX_RETRIES,
                 task_queue=None,
                 http_client=None,
                 logger=None,
                 **kwargs):
        """
        :param name: see the common_crawler.configuration
        :param roots: see the common_crawler.configuration
        :param strict: see the common_crawler.configuration
        :param max_redirect: see the common_crawler.configuration
        :param max_retries: see the common_crawler.configuration
        :param task_queue: the queue for store the link which ready to crawl
        :param http_client: the client for making the request of HTTP
        """
        self.strict = strict
        self.max_redirect = max_redirect
        self.max_retries = max_retries
        self.task_queue = task_queue or self._init_task_queue()
        self.http_client = http_client or self._init_http_client()
        self.logger = logger or logging.getLogger(name)
        self.seen_urls = self._init_seen_urls()
        self.finished_urls = self._init_finished_urls()
        self.__dict__.update(**kwargs)

        func_names = ('add', 'append')
        self.add_to_seen_urls = get_function_by_name(self.seen_urls, func_names)
        self.add_to_finished_urls = get_function_by_name(self.finished_urls, func_names)
        if not callable(self.add_to_seen_urls) or not callable(self.add_to_finished_urls):
            message = """seen_urls and finished_urls must have to one
            function that name is "add" or "append" for adding an element"""
            raise ValueError(message)

        roots = revise_urls(arg_to_iter(roots), strict)
        for root in roots:
            self.add_to_task_queue(root)

        self.logger.info('Crawler(%s) is initialized, the URL queue of start crawl is  %s'
                         % (self.__class__.__name__ + ":" + name, roots))

    @abstractmethod
    def crawl(self, parse_link=None):
        """
        Return a URL that fetched (object Task), each URL is from the task_queue and
        make a request via http_client then parse the response.
        """
        raise NotImplementedError

    @abstractmethod
    def parse_link(self, response):
        """
        Return the parsed data from HTML(response), the priority less than the param parse_link
        of the function crawl(), in other words, this function will not be called if the
        param parse_link of the function crawl() is not None.
        """
        raise NotImplementedError

    @abstractmethod
    def add_to_task_queue(self, url):
        """Add a URL to the task queue if not seen before"""
        raise NotImplementedError

    @abstractmethod
    def _init_task_queue(self):
        raise NotImplementedError

    @abstractmethod
    def _init_http_client(self):
        raise NotImplementedError

    @abstractmethod
    def close(self):
        """Release all acquired resources"""
        raise NotImplementedError

    """
    seen_urls and finished_urls must have to one function that name is "add" or "append" for 
    adding an element and the function that name is "remove" for delete an element.
    """

    @abstractmethod
    def _init_seen_urls(self):
        raise NotImplementedError

    @abstractmethod
    def _init_finished_urls(self):
        raise NotImplementedError

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
