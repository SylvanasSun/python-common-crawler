"""Request and response of HTTP protocol"""

__all__ = ['Response']


class Response(object):
    """
    A Response class represents an HTTP response, which is usually put into
    a object common_crawler.task.Task and be passed on to LinkExtractor for
    extract links.
    """

    __slots__ = [
        'url', 'status', 'charset', 'content_type',
        'content_length', 'reason', 'headers', 'text',
        'selector'
    ]

    def __init__(self, url, status, charset, content_type,
                 content_length, reason, headers, text,
                 selector):
        self.url = url
        self.status = status
        self.charset = charset
        self.content_type = content_type
        self.content_length = content_length
        self.reason = reason
        self.headers = headers
        self.text = text
        self.selector = selector

    def xpath(self, path, **kwargs):
        if not self.selector or not hasattr(self.selector, 'xpath'):
            return None

        return self.selector.xpath(path, **kwargs)

    def __repr__(self):
        return 'Response (%s-%s:%s content <%s:%s>)' \
               % (
                   self.url, self.status, self.reason,
                   self.content_type, self.content_length
               )

    __str__ = __repr__
