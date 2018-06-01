import asyncio

from common_crawler.crawler import Crawler, FetchedUrl
from common_crawler.http import ResponseDataType as type
from common_crawler.http.aiohttp import AioHttpClient
from common_crawler.utils.misc import arg_to_iter
from common_crawler.utils.url import join_url, is_redirect, get_domain

__all__ = ['AsyncCrawler']


class AsyncCrawler(Crawler):
    """
    The class AsyncCrawler is an implementation of the class Crawler base on the asyncio.
    """

    def __init__(self, **kwargs):
        super(self.__class__, self).__init__(**kwargs)

    async def crawl(self, parse_link=None):
        try:
            while True:
                task = await self.task_queue.get()
                task, url = await self._process(task, parse_link)

                # ignore the failed task
                if task is None:
                    self.logger.error('The url %s is invalid' % url)
                elif isinstance(task.exception, Exception):
                    self.logger.error('The url %s is invalid, raise exception %s' % (url, task.exception))
                # if the task is valid
                # return the FetchedUrl to the Engine for extract links and handle parsed data
                else:
                    yield task

                # for record
                self.add_to_finished_urls(task)
                self.task_queue.task_done()
        except asyncio.CancelledError:
            pass

    async def _process(self, task, parse_link):
        """
        Process the url and return the FetchedUrl which contains the parsed data.
        """
        exception = None
        response = None
        url = task.url if task.redirect_num == 0 else task.redirect_url

        # ignore the difference that prefix of HTTP/HTTPS
        domain = get_domain(url)
        if domain in self.seen_urls:
            return None, url
        else:
            self.add_to_seen_urls(domain)

        while task.retries_num < self.max_retries:
            try:
                response = self.http_client.get(url, allow_redirects=False)

                if task.retries_num > 1:
                    self.logger.debug(
                        'Request the url %s has succeeded, tries %s times' % (
                            url, task.retries_num))

                break
            except Exception as error:
                self.logger.debug(
                    'Request the url %s has failed and tried again, tries %s times, raised: %s' % (
                        url, task.retries_num, error))
                exception = error

            task.retries_num += 1

        # all tries is failed
        if task.retries_num == self.max_retries:
            self.logger.error(
                'All attempts to request the url %s have failed and will to ignore this task' % url)
            task.exception = exception
            return task, url

        # get parsed data by the function parse_link(), and handle the redirection
        async with response as resp:
            await self._handle_request_info(task, resp)

            if is_redirect(task.status):
                location = task.headers.get('location', url)
                task.redirect_url = join_url(location, base_url=url)

                if get_domain(task.redirect_url) in self.seen_urls:
                    return None, url

                if task.redirect_num < self.max_redirect:
                    self.logger.info('Redirect to %s from %s ' % (task.redirect_url, url))
                    task.redirect_num += 1
                    # recursive request the redirect url
                    return await self._process(task, parse_link)
                else:
                    self.logger.error('Redirect limit reached for %s from %s' % (task.redirect_url, url))
                    return None, url
            else:
                if parse_link is not None:
                    task.parsed_data = parse_link(resp)
                else:
                    task.parsed_data = await self.parse_link(resp)
                return task, url

    async def _handle_request_info(self, task, response):
        """Packing the information of request into the FetchedUrl."""
        task.status = await self.http_client.get_response_data(response, type.STATUS_CODE)
        task.charset = await self.http_client.get_response_data(response, type.CHARSET)
        task.content_type = await self.http_client.get_response_data(response, type.CONTENT_TYPE)
        task.content_length = await self.http_client.get_response_data(response, type.CONTENT_LENGTH)
        task.reason = await self.http_client.get_response_data(response, type.REASON)
        task.headers = await self.http_client.get_response_data(response, type.HEADERS)

    async def parse_link(self, response):
        """
        Only return the HTML content in the default implementation.
        """
        return await self.http_client.get_response_data(response, type.HTML)

    def add_to_task_queue(self, url):
        urls = arg_to_iter(url)
        for u in urls:
            self.task_queue.put_nowait(
                FetchedUrl(url=u,
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
                           redirect_url=None)
            )
        self.logger.debug('Adding the url %s into the task queue' % urls)

    def _init_task_queue(self):
        return asyncio.Queue()

    def _init_http_client(self):
        return AioHttpClient()

    def _init_seen_urls(self):
        return set()

    def _init_finished_urls(self):
        return []

    async def close(self):
        await self.http_client.close()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
