"""The crawler implements the crawling logic"""
import logging
from abc import ABC, abstractmethod

from common_crawler.configuration import CONFIGURATION
from common_crawler.utils.url import revise_urls

__all__ = ['Crawler', 'FetchedUrl']

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
    is the class FetchedUrl.

    There are several important data structures that are task queue, seen_urls, and finished_urls,
    the task queue be responsible for to store the object FetchedUrl and each element represent a
    crawled URL then component Engine will be extract other links from the FetchedUrl by LinkExtractor
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

        roots = revise_urls(roots, strict)
        for root in roots:
            self.add_to_task_queue(root)

        self.logger.info('Crawler(%s) is initialized, the URL queue of start crawl is  %s'
                         % (self.__class__.__name__ + ":" + name, roots))

    @abstractmethod
    def crawl(self, parse_link=None):
        """
        Return a URL that fetched (object FetchedUrl), each URL is from the task_queue and
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

    def _init_seen_urls(self):
        return set()

    def _init_finished_urls(self):
        return []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


class FetchedUrl(object):
    """
    A fetched URL and it contains parsed data via parse_link(), metadata of the response,
    captured the exception and the number of redirect and retry of URL.
    """

    __slots__ = [
        'url', 'parsed_data', 'status', 'charset',
        'content_type', 'content_length', 'reason',
        'headers', 'exception',
        'redirect_num', 'retries_num', 'redirect_url'
    ]

    def __init__(self, url, parsed_data, status, charset,
                 content_type, content_length,
                 reason, headers, exception,
                 redirect_num, retries_num, redirect_url):
        self.url = url
        self.parsed_data = parsed_data
        self.status = status
        self.charset = charset
        self.content_type = content_type
        self.content_length = content_length
        self.reason = reason
        self.headers = headers
        self.exception = exception
        self.redirect_num = redirect_num
        self.retries_num = retries_num
        self.redirect_url = redirect_url

    def __repr__(self):
        return 'FetchedUrl(%s-%s:%s content <%s:%s>)' \
               % (
                   self.url, self.status, self.reason,
                   self.content_type, self.content_length
               )

    __str__ = __repr__
