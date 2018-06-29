import asyncio
from asyncio import ensure_future

from common_crawler.engines import Engine

__all__ = ['AsyncEngine']


class AsyncEngine(Engine):
    def __init__(self, **kwargs):
        super(self.__class__, self).__init__(**kwargs)
        self.loop = self.__dict__.get('loop', asyncio.get_event_loop())

    def work(self):
        workers = [ensure_future(self._handle(), loop=self.loop)
                   for _ in range(self.config['max_tasks'])]

        self.loop.run_until_complete(self.crawler.task_queue.join())
        for worker in workers:
            worker.cancel()

    async def _handle(self):
        async for t in self.crawler.crawl():
            self.handle(t)

    async def close(self):
        self.pipeline.close()
        await self.crawler.close()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
