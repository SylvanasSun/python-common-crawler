import asyncio
import unittest

from common_crawler.crawler import Crawler
from common_crawler.engines.async import AsyncEngine
from common_crawler.link_extractor import LinkExtractor
from common_crawler.pipeline import Pipeline
from tests.mock import FakedObject


class FakedCrawler(Crawler):
    def __init__(self, **kwargs):
        super(self.__class__, self).__init__(**kwargs)

    async def crawl(self, parse_link=None):
        try:
            while True:
                task = await self.task_queue.get()
                if task is not None:
                    yield task
                self.add_to_finished_urls(task)
                self.task_queue.task_done()
        except asyncio.CancelledError:
            pass

    def parse_link(self, response):
        pass

    def add_to_task_queue(self, url):
        if isinstance(url, str):
            url = [url]

        for u in url:
            self.task_queue.put_nowait(FakedObject(
                url=u,
                parsed_data=None,
                status=None,
                charset=None,
                content_type=None,
                content_length=0,
                reason=None,
                headers=None,
                exception=None,
                redirect_num=0,
                retries_num=0,
                redirect_url=None,
                html=None
            ))

    def _init_task_queue(self):
        return None

    def _init_http_client(self):
        return None

    def _init_seen_urls(self):
        return set()

    def _init_finished_urls(self):
        return []

    async def close(self):
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()


class FakedLinkExtractor(LinkExtractor):
    def __init__(self, **kwargs):
        super(self.__class__, self).__init__(**kwargs)
        self.return_val = FakedObject(url='https://www.link_extractor.com')
        self.count = 0

    def extract_links(self, **kwargs):
        if self.count == 0:
            self.count += 1
            return [self.return_val]
        else:
            return []

    def _process(self, response, encoding='utf-8'):
        pass


class FakedPipeline(Pipeline):
    def __init__(self, **kwargs):
        super(self.__class__, self).__init__(**kwargs)
        self.task = None

    def transmit(self, task, **kwargs):
        self.task = task

    def handle(self, **kwargs):
        pass

    def setup(self, **kwargs):
        pass

    def close(self, **kwargs):
        pass


class TestAsyncEngine(unittest.TestCase):
    def setUp(self):
        self.configuration = {
            'name': 'common_crawler',
            'roots': ('http://www.example.com',),
            'deny_domains': (),
            'allow_domains': (),
            'strict': True,
            'follow': True,
            'allowed_rule': (),
            'denied_rule': (),
            'log_level': 2,
            'log_filename': None,
            'log_format': '%(asctime)s:%(levelname)s:%(message)s',
            'log_init_fn': 'common_crawler.engines._init_logging',
            'max_redirect': 10,
            'max_retries': 4,
            'max_tasks': 100,
            'interval': 1
        }

        self.task = FakedObject(url='https://www.google.com',
                                parsed_data=None,
                                status=200,
                                charset='utf-8',
                                content_type='text/html',
                                content_length=None,
                                reason='OK',
                                headers=None,
                                exception=None,
                                redirect_num=0,
                                retries_num=0,
                                redirect_url=None,
                                html='<html><body><a href="/abc"></a></body></html>')

        self.task_queue = asyncio.Queue()
        self.http_client = FakedObject()
        self.parse_link = lambda x: print('Parsing...')

    def test_load_from_components(self):
        components = {
            'crawler': '%s.%s' % (self.__class__.__module__, FakedCrawler.__name__),
            'link_extractor': '%s.%s' % (self.__class__.__module__, FakedLinkExtractor.__name__),
            'pipeline': '%s.%s' % (self.__class__.__module__, FakedPipeline.__name__)
        }

        engine = AsyncEngine(configuration=self.configuration,
                             components=components,
                             http_client=self.http_client,
                             task_queue=self.task_queue,
                             parse_link=self.parse_link)

        async def judge():
            async with engine:
                self.assertIsNotNone(getattr(engine, 'crawler', None))
                self.assertIsNotNone(getattr(engine, 'link_extractor', None))
                self.assertIsNotNone(getattr(engine, 'pipeline', None))
                self.assertTrue(isinstance(engine.crawler, FakedCrawler))
                self.assertTrue(isinstance(engine.link_extractor, FakedLinkExtractor))
                self.assertTrue(isinstance(engine.pipeline, FakedPipeline))

                self.assertIsNotNone(getattr(engine.crawler, 'task_queue', None))
                self.assertIsNotNone(getattr(engine.crawler, 'http_client', None))
                self.assertIsNotNone(getattr(engine.crawler, 'parse_link', None))
                self.assertEqual(engine.crawler.task_queue, self.task_queue)
                self.assertEqual(engine.crawler.http_client, self.http_client)
                self.assertEqual(engine.crawler.parse_link, self.parse_link)

                task_queue = engine.crawler.task_queue
                self.assertEqual(task_queue.qsize(), 1)
                task = await task_queue.get()
                self.assertEqual(task.url, self.configuration['roots'][0])

        asyncio.get_event_loop().run_until_complete(judge())

    def test_add_links(self):
        engine = self._get_default_engine()

        async def judge():
            async with engine:
                engine.add_links(self.task)

                task_queue = engine.crawler.task_queue
                self.assertEqual(task_queue.qsize(), 1)
                task = await task_queue.get()
                self.assertEqual(task.url, engine.link_extractor.return_val.url)

        asyncio.get_event_loop().run_until_complete(judge())

    def test_add_links_not_follow(self):
        self.configuration['follow'] = False
        engine = self._get_default_engine()

        async def judge():
            async with engine:
                engine.add_links(self.task)

                task_queue = engine.crawler.task_queue
                self.assertEqual(task_queue.qsize(), 0)

        asyncio.get_event_loop().run_until_complete(judge())

    def test_transmit_data(self):
        engine = self._get_default_engine()

        async def judge():
            async with engine:
                engine.transmit_data(self.task)

                pipeline = engine.pipeline
                self.assertEqual(pipeline.task, self.task)

        asyncio.get_event_loop().run_until_complete(judge())

    def test_handle(self):
        engine = self._get_default_engine()

        async def judge():
            async with engine:
                engine.handle(self.task)

                pipeline = engine.pipeline
                self.assertEqual(pipeline.task, self.task)

                task_queue = engine.crawler.task_queue
                self.assertEqual(task_queue.qsize(), 1)
                task = await task_queue.get()
                self.assertEqual(task.url, engine.link_extractor.return_val.url)

        asyncio.get_event_loop().run_until_complete(judge())

    def test_start(self):
        engine = self._get_default_engine()
        engine.crawler.add_to_task_queue(self.configuration['roots'])

        engine.start()

        finished = engine.crawler.finished_urls

        self.assertEqual(len(finished), 2)
        self.assertEqual(finished[0].url, self.configuration['roots'][0])
        self.assertEqual(finished[1].url, engine.link_extractor.return_val.url)

        asyncio.get_event_loop().run_until_complete(engine.close())

    def test_clean_for_finished_urls(self):
        engine = self._get_default_engine()
        engine.crawler.finished_urls = [FakedObject(url='f'),
                                        FakedObject(url='g'),
                                        None,
                                        FakedObject(url='d'),
                                        None,
                                        FakedObject(url='a')]

        engine._clean_for_finished_urls()
        self.assertEqual(len(engine.crawler.finished_urls), 4)
        self.assertEqual(engine.crawler.finished_urls[0].url, 'a')
        self.assertEqual(engine.crawler.finished_urls[1].url, 'd')
        self.assertEqual(engine.crawler.finished_urls[2].url, 'f')
        self.assertEqual(engine.crawler.finished_urls[3].url, 'g')

    def _get_default_engine(self):
        return AsyncEngine(configuration=self.configuration,
                           crawler=FakedCrawler(http_client=self.http_client,
                                                task_queue=self.task_queue,
                                                parse_link=self.parse_link,
                                                ),
                           link_extractor=FakedLinkExtractor(),
                           pipeline=FakedPipeline())


if __name__ == '__main__':
    unittest.main()
