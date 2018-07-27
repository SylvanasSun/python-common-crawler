import asyncio
import unittest
from unittest import mock

from common_crawler.http.client.aiohttp import AioHttpClient
from tests.mock import FakedObject

_TARGET_URL = 'https://www.example.com/hello'

_MOCKED_TARGET = '%s.%s' % (AioHttpClient.__module__, AioHttpClient.__name__)

_LOOP = asyncio.get_event_loop()


class TestAioHttpClient(unittest.TestCase):
    """Test for common_crawler.http.aiohttp.AioHttpClient"""

    @mock.patch(_MOCKED_TARGET + '.request')
    def test_request(self, mocked):
        status = 200
        method = 'GET'
        mocked.return_value = FakedObject(status=status)

        async def work():
            async with AioHttpClient() as client:
                async with client.request(method=method, url=_TARGET_URL) as resp:
                    self.assertEqual(status, resp.status)

        _LOOP.run_until_complete(work())
        mocked.assert_called_once_with(method=method, url=_TARGET_URL)

    @mock.patch(_MOCKED_TARGET + '.get')
    def test_get(self, mocked):
        status = 200
        mocked.return_value = FakedObject(status=200)

        async def work():
            async with AioHttpClient() as client:
                async with client.get(url=_TARGET_URL) as resp:
                    self.assertEqual(status, resp.status)

        _LOOP.run_until_complete(work())
        mocked.assert_called_once_with(url=_TARGET_URL)

    @mock.patch(_MOCKED_TARGET + '.post')
    def test_post(self, mocked):
        status = 200
        mocked.return_value = FakedObject(status=status)

        async def work():
            async with AioHttpClient() as client:
                async with client.post(url=_TARGET_URL) as resp:
                    self.assertEqual(status, resp.status)

        _LOOP.run_until_complete(work())
        mocked.assert_called_once_with(url=_TARGET_URL)

    @mock.patch(_MOCKED_TARGET + '.put')
    def test_put(self, mocked):
        status = 200
        mocked.return_value = FakedObject(status=status)

        async def work():
            async with AioHttpClient() as client:
                async with client.put(url=_TARGET_URL) as resp:
                    self.assertEqual(status, resp.status)

        _LOOP.run_until_complete(work())
        mocked.assert_called_once_with(url=_TARGET_URL)

    @mock.patch(_MOCKED_TARGET + '.delete')
    def test_delete(self, mocked):
        status = 200
        mocked.return_value = FakedObject(status=status)

        async def work():
            async with AioHttpClient() as client:
                async with client.delete(url=_TARGET_URL) as resp:
                    self.assertEqual(status, resp.status)

        _LOOP.run_until_complete(work())
        mocked.assert_called_once_with(url=_TARGET_URL)

    @mock.patch(_MOCKED_TARGET + '.options')
    def test_options(self, mocked):
        status = 200
        mocked.return_value = FakedObject(status=status)

        async def work():
            async with AioHttpClient() as client:
                async with client.options(url=_TARGET_URL) as resp:
                    self.assertEqual(status, resp.status)

        _LOOP.run_until_complete(work())
        mocked.assert_called_once_with(url=_TARGET_URL)

    @mock.patch(_MOCKED_TARGET + '.head')
    def test_head(self, mocked):
        status = 200
        mocked.return_value = FakedObject(status=status)

        async def work():
            async with AioHttpClient() as client:
                async with client.head(url=_TARGET_URL) as resp:
                    self.assertEqual(status, resp.status)

        _LOOP.run_until_complete(work())
        mocked.assert_called_once_with(url=_TARGET_URL)

    @mock.patch(_MOCKED_TARGET + '.patch')
    def test_patch(self, mocked):
        status = 200
        mocked.return_value = FakedObject(status=status)

        async def work():
            async with AioHttpClient() as client:
                async with client.patch(url=_TARGET_URL) as resp:
                    self.assertEqual(status, resp.status)

        _LOOP.run_until_complete(work())
        mocked.assert_called_once_with(url=_TARGET_URL)

    def test_get_response(self):
        from common_crawler.http import Response
        from lxml.etree import _Element

        async def text():
            return 'HTML'

        response = FakedObject(url=_TARGET_URL,
                               status=200,
                               charset='utf-8',
                               content_type='text/html',
                               content_length=233,
                               reason='OK',
                               headers={'connection': 'keep-alive'})

        response.text = text

        async def work():
            async with AioHttpClient() as client:
                expected = await client.get_response(response)

                self.assertTrue(isinstance(expected, Response))

                self.assertTrue(isinstance(expected.url, str))
                self.assertEqual(_TARGET_URL, expected.url)

                self.assertTrue(isinstance(expected.text, str))
                self.assertEqual('HTML', expected.text)

                self.assertTrue(isinstance(expected.status, int))
                self.assertEqual(expected.status, 200)

                self.assertTrue(isinstance(expected.charset, str))
                self.assertEqual(expected.charset, 'utf-8')

                self.assertTrue(isinstance(expected.content_type, str))
                self.assertEqual(expected.content_type, 'text/html')

                self.assertTrue(isinstance(expected.content_length, int))
                self.assertEqual(expected.content_length, 233)

                self.assertTrue(isinstance(expected.reason, str))
                self.assertEqual(expected.reason, 'OK')

                self.assertTrue(isinstance(expected.headers, dict))
                self.assertTrue('connection' in expected.headers)
                self.assertEqual(expected.headers['connection'], 'keep-alive')

                self.assertTrue(isinstance(expected.selector, _Element))

        _LOOP.run_until_complete(work())


if __name__ == '__main__':
    unittest.main()
