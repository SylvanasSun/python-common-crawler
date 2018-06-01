import asyncio
import unittest
from unittest.mock import patch

from common_crawler.crawler.async import AsyncCrawler
from tests.mock import FakedObject

_MOCKED_TARGET = 'common_crawler.http.aiohttp.AioHttpClient.get'

_URL = 'https://www.example.com'

_STATUS = 200

_HEADERS = {'connection': 'keep-alive'}

_CHARSET = 'utf-8'

_CONTENT_TYPE = 'text/html'

_CONTENT_LENGTH = 233

_REASON = 'OK'

_BODY = '<html><body><h1>Example</h1></body></html>'


async def _TEXT():
    return _BODY


class AsyncCrawlerLauncher(object):
    def __init__(self, crawler, work, max_task=10):
        self.max_task = max_task
        self.work = work
        self.crawler = crawler
        self.loop = asyncio.get_event_loop()

    def run(self):
        async def w():
            async with self.crawler as crawler:
                tasks = [asyncio.Task(self.work(crawler), loop=self.loop)
                         for _ in range(self.max_task)]
                await crawler.task_queue.join()
                for task in tasks:
                    task.cancel()

        self.loop.run_until_complete(w())


class AsyncCrawlerTest(unittest.TestCase):
    def setUp(self):
        self.response = FakedObject(url=_URL,
                                    status=_STATUS,
                                    headers=_HEADERS,
                                    charset=_CHARSET,
                                    content_type=_CONTENT_TYPE,
                                    content_length=_CONTENT_LENGTH,
                                    reason=_REASON)
        self.response.text = _TEXT

    @patch(_MOCKED_TARGET)
    def test_crawl(self, mocked):
        mocked.return_value = self.response

        async def work(crawler):
            global t
            async for t in crawler.crawl():
                t = t
                self.assertEqual(_URL, t.url)
                self.assertEqual(_STATUS, t.status)
                self.assertEqual(_HEADERS.get('connection'), t.headers.get('connection'))
                self.assertEqual(0, t.retries_num)
                self.assertEqual(0, t.redirect_num)
                self.assertEqual(_CONTENT_TYPE, t.content_type)
                self.assertEqual(_CONTENT_LENGTH, t.content_length)
                self.assertEqual(_REASON, t.reason)
                self.assertEqual(_CHARSET, t.charset)
                # default parse_link() will to extract HTML
                self.assertEqual(_BODY, t.parsed_data)
            # seen_urls only store the domain name
            self.assertTrue(_URL[_URL.find('www'):] in crawler.seen_urls)
            self.assertTrue(t in crawler.finished_urls)

        crawler = AsyncCrawler(roots=_URL)
        launcher = AsyncCrawlerLauncher(crawler=crawler, work=work)
        launcher.run()

    @patch(_MOCKED_TARGET)
    def test_crawl_as_redirect(self, mocked):
        mocked.return_value = FakedObject(url=_URL,
                                          status=301,
                                          headers={'location': 'https://www.python.org'},
                                          charset=_CHARSET,
                                          content_type=_CONTENT_TYPE,
                                          content_length=_CONTENT_LENGTH,
                                          reason=_REASON)
        list = []

        async def work(crawler):
            async for t in crawler.crawl():
                list.append(t)

        crawler = AsyncCrawler(roots=_URL)
        launcher = AsyncCrawlerLauncher(crawler=crawler, work=work)
        launcher.run()
        self.assertEqual(0, len(list))

    def test_parse_link(self):
        crawler = AsyncCrawler()

        async def work():
            expected = await self.response.text()
            actual = await crawler.parse_link(self.response)
            self.assertEqual(expected, actual)

        asyncio.get_event_loop().run_until_complete(work())

    def test_to_task_queue(self):
        crawler = AsyncCrawler()

        async def work():
            crawler.add_to_task_queue(_URL)
            self.assertEqual(1, crawler.task_queue.qsize())
            url_2 = 'https://www.python.org'
            crawler.add_to_task_queue(url_2)
            self.assertEqual(2, crawler.task_queue.qsize())
            task = await crawler.task_queue.get()
            self.assertEqual(_URL, task.url)
            task = await crawler.task_queue.get()
            self.assertEqual(url_2, task.url)

        asyncio.get_event_loop().run_until_complete(work())


if __name__ == '__main__':
    unittest.main()
