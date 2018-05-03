"""The implementation of HttpClient by aiohttp"""

import json

from aiohttp import ClientSession, ClientRequest, ClientWebSocketResponse, http, ClientResponse

from common_crawler.http import HttpClient
from common_crawler.utils.misc import dynamic_import, DynamicImportReturnType

__all__ = ['AioHttpClient']

sentinel = dynamic_import('aiohttp.helpers.sentinel', DynamicImportReturnType.VARIABLE)


class AioHttpClient(HttpClient):
    def __init__(self, *, connector=None,
                 loop=None, cookies=None,
                 headers=None, skip_auto_headers=None,
                 auth=None, json_serialize=json.dumps,
                 request_class=ClientRequest,
                 response_class=ClientResponse,
                 ws_response_class=ClientWebSocketResponse,
                 version=http.HttpVersion11,
                 cookie_jar=None, connector_owner=True,
                 raise_for_status=False,
                 read_timeout=sentinel, conn_timeout=None,
                 auto_decompress=True, trust_env=False, **kwargs):
        """
        The class packaging a class ClientSession to perform HTTP request and manager that these HTTP connection.

        For details of the params: http://aiohttp.readthedocs.io/en/stable/client_advanced.html#client-session
        """
        super(AioHttpClient, self).__init__(**kwargs)
        self.client = ClientSession(connector=connector,
                                    loop=loop,
                                    cookies=cookies,
                                    headers=headers,
                                    skip_auto_headers=skip_auto_headers,
                                    auth=auth,
                                    json_serialize=json_serialize,
                                    request_class=request_class,
                                    response_class=response_class,
                                    ws_response_class=ws_response_class,
                                    version=version,
                                    cookie_jar=cookie_jar,
                                    connector_owner=connector_owner,
                                    raise_for_status=raise_for_status,
                                    read_timeout=read_timeout,
                                    conn_timeout=conn_timeout,
                                    auto_decompress=auto_decompress,
                                    trust_env=trust_env)

    def request(self, method, url, *args, **kwargs):
        return self.client.request(method=method, url=url, **kwargs)

    def get(self, url, *args, **kwargs):
        allow_redirects = self._get_from_kwargs(kwargs=kwargs,
                                                item_name='allow_redirects',
                                                default_val=True)
        return self.client.get(url=url,
                               allow_redirects=allow_redirects,
                               **kwargs)

    def post(self, url, *args, data=None, **kwargs):
        return self.client.post(url=url, data=data, **kwargs)

    def put(self, url, *args, data=None, **kwargs):
        return self.client.put(url=url, data=data, **kwargs)

    def delete(self, url, *args, **kwargs):
        return self.client.delete(url=url, **kwargs)

    def options(self, url, *args, **kwargs):
        allow_redirects = self._get_from_kwargs(kwargs=kwargs,
                                                item_name='allow_redirects',
                                                default_val=True)
        return self.client.options(url=url,
                                   allow_redirects=allow_redirects,
                                   **kwargs)

    def head(self, url, *args, **kwargs):
        allow_redirects = self._get_from_kwargs(kwargs=kwargs,
                                                item_name='allow_redirects',
                                                default_val=False)
        return self.client.head(url=url,
                                allow_redirects=allow_redirects,
                                **kwargs)

    def patch(self, url, *args, data=None, **kwargs):
        return self.client.patch(url=url, data=data, **kwargs)

    def close(self):
        self.client.close()

    def _get_from_kwargs(self, kwargs, item_name, default_val):
        return kwargs.get(item_name, default_val)

    def __aenter__(self):
        return self

    def __aexit__(self, exc_type, exc_val, exc_tb):
        yield from self.close()