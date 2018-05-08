import asyncio
import unittest

from common_crawler.http.aiohttp import AioHttpClient

_TARGET_URL = 'https://www.python.org'


def _run(coro):
    asyncio.get_event_loop().run_until_complete(coro)


class TestAioHttpClient(unittest.TestCase):
    """Test for common_crawler.http.aiohttp.AioHttpClient"""

    def test_request(self):
        async def work():
            async with AioHttpClient() as client:
                async with client.request(method='GET', url=_TARGET_URL) as resp:
                    self.assertEqual(resp.status, 200)

        _run(work())

    def test_get(self):
        async def work():
            async with AioHttpClient() as client:
                async with client.get(url=_TARGET_URL) as resp:
                    self.assertEqual(resp.status, 200)

        _run(work())

    def test_post(self):
        async def work():
            async with AioHttpClient() as client:
                async with client.post(url=_TARGET_URL) as resp:
                    self.assertEqual(resp.status, 403)

        _run(work())

    def test_put(self):
        async def work():
            async with AioHttpClient() as client:
                async with client.put(url=_TARGET_URL) as resp:
                    self.assertEqual(resp.status, 403)

        _run(work())

    def test_delete(self):
        async def work():
            async with AioHttpClient() as client:
                async with client.delete(url=_TARGET_URL) as resp:
                    self.assertEqual(resp.status, 403)

        _run(work())

    def test_options(self):
        async def work():
            async with AioHttpClient() as client:
                async with client.options(url=_TARGET_URL) as resp:
                    self.assertEqual(resp.status, 200)

        _run(work())

    def test_head(self):
        async def work():
            async with AioHttpClient() as client:
                async with client.head(url=_TARGET_URL) as resp:
                    self.assertEqual(resp.status, 200)

        _run(work())

    def test_patch(self):
        async def work():
            async with AioHttpClient() as client:
                async with client.patch(url=_TARGET_URL) as resp:
                    self.assertEqual(resp.status, 403)

        _run(work())

    def test_get_from_kwargs(self):
        kw = {'a': 0, 'b': 1}
        client = AioHttpClient()
        r = client._get_from_kwargs(kw, 'a', None)
        self.assertEqual(r, kw['a'])
        r = client._get_from_kwargs(kw, 'b', None)
        self.assertEqual(r, kw['b'])
        r = client._get_from_kwargs(kw, 'c', None)
        self.assertEqual(r, None)
        client.close()

    def test_get_response_data(self):
        from common_crawler.http import ResponseDataType as type
        from multidict import CIMultiDictProxy

        async def work():
            async with AioHttpClient() as client:
                async with client.get(url=_TARGET_URL) as resp:
                    html = await client.get_response_data(resp, type.HTML)
                    self.assertTrue(isinstance(html, str))

                    status = await client.get_response_data(resp, type.STATUS_CODE)
                    self.assertEqual(status, 200)

                    charset = await client.get_response_data(resp, type.CHARSET)
                    self.assertEqual(charset, 'utf-8')

                    content_type = await client.get_response_data(resp, type.CONTENT_TYPE)
                    self.assertEqual(content_type, 'text/html')

                    content_length = await client.get_response_data(resp, type.CONTENT_LENGTH)
                    self.assertTrue(isinstance(content_length, int))

                    reason = await client.get_response_data(resp, type.REASON)
                    self.assertEqual(reason, 'OK')

                    headers = await client.get_response_data(resp, type.HEADERS)
                    self.assertTrue(isinstance(headers, CIMultiDictProxy))

                    with self.assertRaises(ValueError):
                        await client.get_response_data(resp, 'something')

        _run(work())


if __name__ == '__main__':
    unittest.main()
