import asyncio
import unittest

from common_crawler.http.aiohttp import AioHttpClient

_TARGET_URL = 'https://www.python.org'


def _run(coro):
    asyncio.get_event_loop().run_until_complete(coro)


class TestAioHttpClient(unittest.TestCase):
    """Test for common_crawler.http.aiohttp.AioHttpClient"""

    def setUp(self):
        self.client = AioHttpClient()

    def test_request(self):
        async def work():
            async with self.client.request(method='GET', url=_TARGET_URL) as resp:
                self.assertEqual(resp.status, 200)

        _run(work())

    def test_get(self):
        async def work():
            async with self.client.get(url=_TARGET_URL) as resp:
                self.assertEqual(resp.status, 200)

        _run(work())

    def test_post(self):
        async def work():
            async with self.client.post(url=_TARGET_URL) as resp:
                self.assertEqual(resp.status, 403)

        _run(work())

    def test_put(self):
        async def work():
            async with self.client.put(url=_TARGET_URL) as resp:
                self.assertEqual(resp.status, 403)

        _run(work())

    def test_delete(self):
        async def work():
            async with self.client.delete(url=_TARGET_URL) as resp:
                self.assertEqual(resp.status, 403)

        _run(work())

    def test_options(self):
        async def work():
            async with self.client.options(url=_TARGET_URL) as resp:
                self.assertEqual(resp.status, 200)

        _run(work())

    def test_head(self):
        async def work():
            async with self.client.head(url=_TARGET_URL) as resp:
                self.assertEqual(resp.status, 200)

        _run(work())

    def test_patch(self):
        async def work():
            async with self.client.patch(url=_TARGET_URL) as resp:
                self.assertEqual(resp.status, 403)

        _run(work())

    def test_get_from_kwargs(self):
        kw = {'a': 0, 'b': 1}
        r = self.client._get_from_kwargs(kw, 'a', None)
        self.assertEqual(r, kw['a'])
        r = self.client._get_from_kwargs(kw, 'b', None)
        self.assertEqual(r, kw['b'])
        r = self.client._get_from_kwargs(kw, 'c', None)
        self.assertEqual(r, None)

    def tearDown(self):
        self.client.close()


if __name__ == '__main__':
    unittest.main()
