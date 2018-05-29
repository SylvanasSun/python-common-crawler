import asyncio
import unittest
from unittest import mock

from common_crawler.http.aiohttp import AioHttpClient
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

    def test_get_response_data(self):
        from common_crawler.http import ResponseDataType as type

        async def text():
            return 'HTML'

        response = FakedObject(status=200,
                               charset='utf-8',
                               content_type='text/html',
                               content_length=233,
                               reason='OK',
                               headers={'connection': 'keep-alive'})

        response.text = text

        async def work():
            async with AioHttpClient() as client:
                html = await client.get_response_data(response, type.HTML)
                self.assertTrue(isinstance(html, str))
                self.assertEqual('HTML', html)

                status = await client.get_response_data(response, type.STATUS_CODE)
                self.assertTrue(isinstance(status, int))
                self.assertEqual(status, 200)

                charset = await client.get_response_data(response, type.CHARSET)
                self.assertTrue(isinstance(charset, str))
                self.assertEqual(charset, 'utf-8')

                content_type = await client.get_response_data(response, type.CONTENT_TYPE)
                self.assertTrue(isinstance(content_type, str))
                self.assertEqual(content_type, 'text/html')

                content_length = await client.get_response_data(response, type.CONTENT_LENGTH)
                self.assertTrue(isinstance(content_length, int))
                self.assertEqual(content_length, 233)

                reason = await client.get_response_data(response, type.REASON)
                self.assertTrue(isinstance(reason, str))
                self.assertEqual(reason, 'OK')

                headers = await client.get_response_data(response, type.HEADERS)
                self.assertTrue(isinstance(headers, dict))
                self.assertTrue('connection' in headers)
                self.assertEqual(headers['connection'], 'keep-alive')

                with self.assertRaises(ValueError):
                    await client.get_response_data(response, 'something')

        _LOOP.run_until_complete(work())


if __name__ == '__main__':
    unittest.main()
