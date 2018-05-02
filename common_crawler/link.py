"""Defines the link object for LinkExtractor"""
from common_crawler.utils.misc import verify_variable_type


class Link(object):
    """
    The object represent an extracted link.
    """

    __slots__ = ['url', 'text']

    def __init__(self, url, text=''):
        verify_variable_type(url, str, 'Link url must be str objects')
        self.url = url
        self.text = text

    def __eq__(self, other):
        return self.url == other.url and self.text == other.text

    def __hash__(self):
        h = 0
        for _, v in self.__dict__.items():
            h = 31 * h + v
        return h

    def __repr__(self):
        return 'Link(url=%s, text=%s)' % (self.url, self.text)

    __str__ = __repr__
