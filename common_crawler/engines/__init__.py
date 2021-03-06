"""The engine for start the crawler system, it assembles all components then start crawling."""

import logging
import sys
import time
from abc import ABC, abstractmethod

from common_crawler.configuration import CONFIGURATION, COMPONENTS_CONFIG
from common_crawler.crawler import Crawler
from common_crawler.link_extractor import LinkExtractor
from common_crawler.pipeline import Pipeline
from common_crawler.utils.misc import verify_configuration, dynamic_import, DynamicImportReturnType as ReturnType

__all__ = ['Engine']


def _init_logging(configuration):
    """
    The default log system initialization function, it is initialized according to the
    configuration item in the configuration file.

    :param configuration: the configuration usually comes from configuration.py
    :return an instance of logger that output to standard output and file
    when specified a filename in the configuration
    """
    levels = [logging.ERROR, logging.WARN, logging.INFO, logging.DEBUG]
    log_level = levels[min(configuration.get('log_level', 2), len(levels) - 1)]
    log_format = configuration.get('log_format', None)
    log_formatter = None

    if isinstance(log_format, str):
        log_formatter = logging.Formatter(fmt=log_format)
        logging.basicConfig(level=log_level, format=log_format)
    else:
        logging.basicConfig(level=log_level)

    logger = logging.getLogger(configuration.get('name', 'common_crawler'))
    log_filename = configuration.get('log_filename', None)
    if isinstance(log_filename, str):
        handle = logging.FileHandler(filename=log_filename)
        handle.setLevel(log_level)
        if log_formatter is not None:
            handle.setFormatter(log_formatter)
        logger.addHandler(handle)

    return logger


class Engine(ABC):
    """
    The abstract class of the engine defines the behavior that needs to be followed of each Engine class,
    an Engine should be able to load configuration (from the command line or constructor)
    then configure each component to enable them to work together finally start crawler system for crawling.
    """

    def __init__(self,
                 configuration=CONFIGURATION,
                 components=COMPONENTS_CONFIG,
                 crawler=None,
                 http_client=None,
                 task_queue=None,
                 link_extractor=None,
                 parse_link=None,
                 pipeline=None,
                 **kwargs):
        """
        Load the configuration to initialize the component.

        :param configuration: the configuration usually comes from configuration.py

        :param components: param "components" is a dictionary that configuration of the components,
        default config item please refer to configuration.COMPONENTS_CONFIG

        :param crawler: the crawler is for crawling url then return an object Task
        to Engine for extract link and handle data, the class must be a subclass of
        common_crawler.crawler.Crawler, if it is None will create a crawler by
        components['crawler']

        :param http_client: the http_client is for making an HTTP request and must be a subclass
        of HttpClient, this param will be delivered to Crawler and if it is None will create a
        HttpClient by means of the function _init_http_client() in the Crawler

        :param task_queue: the task_queue is queue which contains tasks and each task is an
        object Task, this param will be delivered to Crawler and if it is None will
        create a task queue by means of the function _init_task_queue() in the Crawler

        :param link_extractor: the link_extractor is for extract link from a specified response
        and it must be a subclass of common_crawler.link_extractor.LinkExtractor, about rules
        of this action, is set in the CONFIGURATION such as deny_domains, allow_domains and so on
        if this param is None will be going to load from components['link_extractor']

        :param parse_link: the parse_link is a function for handle data by a specified response
        (is a unary function and param must is a response of HTTP), it should is a function that
        you need to customized implement and this param will be delivered to Crawler and if it
        is None will invoke a function parse_link() of Crawler (default implement)

        :param pipeline: the pipeline is for transmitting parsed data to a place that you want it
        and must be a subclass of common_crawler.pipeline.Pipeline, if this param is None will be
        going to load from components['pipeline']

        :param kwargs: additional configuration item that has precedence over CONFIGURATION
        """
        self.config = {}
        if verify_configuration(configuration):
            self.config.update(configuration)

        # cover the config item with kwargs
        to_remove = []
        for k, v in kwargs.items():
            if k in CONFIGURATION:
                to_remove.append(k)
                self.config.__setitem__(k, v)

        for k in to_remove:
            kwargs.pop(k)

        self.__dict__.update(kwargs)

        try:
            self.logger = dynamic_import(self.config.get('log_init_fn', None),
                                         ReturnType.FUNCTION,
                                         self.config)
        except Exception as e:
            print('The dynamic function call has an error: %s' % e)
            print('next, call the default function for initialize log system.')
            self.logger = _init_logging(self.config)

        self.crawler = crawler if crawler else dynamic_import(components['crawler'],
                                                              ReturnType.CLASS,
                                                              name=self.config['name'],
                                                              roots=self.config['roots'],
                                                              strict=self.config['strict'],
                                                              max_redirect=self.config['max_redirect'],
                                                              max_retries=self.config['max_retries'],
                                                              task_queue=task_queue,
                                                              http_client=http_client,
                                                              logger=self.logger)

        if callable(parse_link):
            self.crawler.parse_link = parse_link

        if not isinstance(self.crawler, Crawler):
            raise ValueError('The crawler is invalid and must be a subclass of %s.%s, got %s.%s'
                             % (Crawler.__module__,
                                Crawler.__name__,
                                self.crawler.__class__.__module__,
                                self.crawler.__class__.__name__)
                             )

        self.link_extractor = link_extractor if link_extractor else dynamic_import(components['link_extractor'],
                                                                                   ReturnType.CLASS,
                                                                                   allow=self.config['allowed_rule'],
                                                                                   deny=self.config['denied_rule'],
                                                                                   allow_domains=self.config[
                                                                                       'allow_domains'],
                                                                                   deny_domains=self.config[
                                                                                       'deny_domains'])

        if not isinstance(self.link_extractor, LinkExtractor):
            raise ValueError('The link extractor is invalid and must be a subclass of %s.%s, got %s.%s'
                             % (LinkExtractor.__module__,
                                LinkExtractor.__name__,
                                self.link_extractor.__class__.__module__,
                                self.link_extractor.__class__.__name__)
                             )

        self.pipeline = pipeline if pipeline else dynamic_import(components['pipeline'],
                                                                 ReturnType.CLASS)

        if not isinstance(self.pipeline, Pipeline):
            raise ValueError('The pipeline is invalid and must be a subclass of %s.%s, got %s.%s'
                             % (Pipeline.__module__,
                                Pipeline.__name__,
                                self.pipeline.__class__.__module__,
                                self.pipeline.__class__.__name__)
                             )

    def start(self):
        try:
            self.start_time = time.time()
            self.logger.info('The Crawler Engine<%s.%s> starts...'
                             % (self.__module__, self.__class__.__name__))

            self.show_config_info()
            self.work()
        except KeyboardInterrupt:
            sys.stderr.flush()
            message = '\nInterrupted by keyboard\n'
            print(message)
            self.logger.error(message)
        finally:
            self.end_time = time.time()
            self.reporting()

    def show_config_info(self):
        self.logger.info('[CONFIG INFORMATION] ----> ')
        for k, v in self.config.items():
            self.logger.info('[ITEM]: %s - %s' % (k, v))

        self.logger.info('------------------------------------')
        self.logger.info('[CRAWLER]: %s.%s' % (self.crawler.__module__, self.crawler.__class__.__name__))

        http_client = self.crawler.http_client
        self.logger.info('[HTTP CLIENT]: %s.%s' % (http_client.__module__, http_client.__class__.__name__))

        task_queue = self.crawler.task_queue
        self.logger.info('[TASK QUEUE]: %s.%s' % (task_queue.__module__, task_queue.__class__.__name__))

        self.logger.info(
            '[LINK EXTRACTOR]: %s.%s' % (self.link_extractor.__module__, self.link_extractor.__class__.__name__))

        parse_link = self.crawler.parse_link
        self.logger.info('[PARSE LINK]: %s.%s' % (parse_link.__module__, parse_link.__name__))

        self.logger.info('[PIPELINE]: %s.%s' % (self.pipeline.__module__, self.pipeline.__class__.__name__))

        self.logger.info('-------------------------------------')
        self.logger.info('[CONFIG INFORMATION] <---- ')

    def reporting(self):
        """Reporting the info that finished the task with crawler.finished_urls"""
        finished = self._clean_for_finished_urls()

        self.logger.info('--------- Finished task ---------')
        self.logger.info('The number of the finished task: %s' % len(finished))
        for t in finished:
            response = t.response

            self.logger.info('Task(%s) - %s<%s>:%s content: %s<%s> retries %s redirects %s'
                             % ('Invalid, error: %s' % t.exception if t.exception else 'Valid',
                                t.url, response.status, response.reason,
                                response.content_type, response.content_length,
                                t.retries_num, t.redirect_num))

        self.logger.info('--------- Total time %ss ---------' % int(self.start_time - self.end_time))

    def _clean_for_finished_urls(self):
        finished = [t for t in self.crawler.finished_urls if t is not None]
        finished.sort(key=lambda t: t.url)
        self.crawler.finished_urls = finished
        return finished

    @abstractmethod
    def work(self):
        """The concrete logic that is implemented by a subclass"""
        raise NotImplementedError

    def handle(self, task):
        """
        Add links to the task queue for next crawl if config item "follow" is True
        and transmit data when got a task from Crawler then sleep for a while by the interval.

        Notice!!! each subclass must call this function when got a task in the function work().

        :param task: a task return from Crawler.crawl()
        """
        if self.config['follow']:
            self.add_links(task)

        self.transmit_data(task)

        interval = self.config['interval']
        if interval > 0:
            time.sleep(interval)

    def add_links(self, task):
        """
        Add the links to the task queue for next crawl.

        :param task: a task return from Crawler.crawl()
        """
        response = task.response
        encoding = response.charset if response.charset else 'utf-8'
        links = self.link_extractor.extract_links(response=response, encoding=encoding)
        links = [l.url for l in links]
        self.crawler.add_to_task_queue(links)

    def transmit_data(self, task):
        """
        Transmit that parsed data by default pipeline SimpleFilePipeline,
        you may need to overwrite this function if the pipeline is not default.

        :param task: a task return from Crawler.crawl()
        """
        response = task.response
        self.pipeline.transmit(task,
                               dirname='data',
                               encode=response.charset if response.charset else 'utf-8')

    @abstractmethod
    def close(self):
        raise NotImplementedError

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
