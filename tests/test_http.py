import asyncio
import unittest

from aioresponses import aioresponses

from common_crawler.http.aiohttp import AioHttpClient

_TARGET_URL = 'https://www.example.com'

_LOOP = asyncio.get_event_loop()


class TestAioHttpClient(unittest.TestCase):
    """Test for common_crawler.http.aiohttp.AioHttpClient"""

    @aioresponses()
    def test_request(self, mocked):
        async def work():
            async with AioHttpClient() as client:
                mocked.get(_TARGET_URL, status=200)
                async with client.request(method='GET', url=_TARGET_URL) as resp:
                    self.assertEqual(resp.status, 200)

        _LOOP.run_until_complete(work())

    @aioresponses()
    def test_get(self, mocked):
        async def work():
            async with AioHttpClient() as client:
                mocked.get(_TARGET_URL, status=200)
                async with client.get(_TARGET_URL) as resp:
                    self.assertEqual(resp.status, 200)

        _LOOP.run_until_complete(work())

    @aioresponses()
    def test_post(self, mocked):
        async def work():
            async with AioHttpClient() as client:
                mocked.post(_TARGET_URL, status=200)
                async with client.post(url=_TARGET_URL) as resp:
                    self.assertEqual(resp.status, 200)

        _LOOP.run_until_complete(work())

    @aioresponses()
    def test_put(self, mocked):
        async def work():
            async with AioHttpClient() as client:
                mocked.put(_TARGET_URL, status=200)
                async with client.put(url=_TARGET_URL) as resp:
                    self.assertEqual(resp.status, 200)

        _LOOP.run_until_complete(work())

    @aioresponses()
    def test_delete(self, mocked):
        async def work():
            async with AioHttpClient() as client:
                mocked.delete(_TARGET_URL, status=200)
                async with client.delete(url=_TARGET_URL) as resp:
                    self.assertEqual(resp.status, 200)

        _LOOP.run_until_complete(work())

    @aioresponses()
    def test_options(self, mocked):
        async def work():
            async with AioHttpClient() as client:
                mocked.options(_TARGET_URL, status=200)
                async with client.options(url=_TARGET_URL) as resp:
                    self.assertEqual(resp.status, 200)

        _LOOP.run_until_complete(work())

    @aioresponses()
    def test_head(self, mocked):
        async def work():
            async with AioHttpClient() as client:
                mocked.head(_TARGET_URL, status=200)
                async with client.head(url=_TARGET_URL) as resp:
                    self.assertEqual(resp.status, 200)

        _LOOP.run_until_complete(work())

    @aioresponses()
    def test_patch(self, mocked):
        async def work():
            async with AioHttpClient() as client:
                mocked.patch(_TARGET_URL, status=200)
                async with client.patch(url=_TARGET_URL) as resp:
                    self.assertEqual(resp.status, 200)

        _LOOP.run_until_complete(work())

    def test_get_response_data(self):
        from common_crawler.http import ResponseDataType as type

        class Response(object):
            def __init__(self, **kwargs):
                self.__dict__.update(kwargs)

            async def text(self):
                return 'HTML'

        response = Response(status=200,
                            charset='utf-8',
                            content_type='text/html',
                            content_length=233,
                            reason='OK',
                            headers={'connection': 'keep-alive'})

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
