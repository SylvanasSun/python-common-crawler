import unittest

from lxml import etree

from common_crawler.link import Link
from common_crawler.link_extractor.lxml import LxmlLinkExtractor


class TestLxmlLinkExtractor(unittest.TestCase):
    """Test for common_crawler.link_extractor.lxml.LxmlLinkExtractor"""

    def setUp(self):
        allow = ('http[s]?:\/\/www.google.com\/?\w*')
        deny = ('http[s]?:\/\/www.google.com\/?hello')
        deny_domains = ['www.amazon.com']
        deny_extensions = ['mp3', 'pdf', 'ppt']
        html = '''
            <html>
                <head></head>
                <body>
                    <a href="https://www.google.com/">Google</a>
                    <a href="https://www.google.com/">Google2</a>
                    <a href="/python">Python</a>
                    <a href="/world">World</a>
                </body>
            </html>
        '''

        class Response(object):
            def __init__(self, url, text):
                self.url = url
                self.text = text

        response = Response(url='https://www.google.com', text=html)
        self.response = response
        self.linkExtractor = LxmlLinkExtractor(allow=allow,
                                               deny=deny,
                                               deny_domains=deny_domains,
                                               deny_extensions=deny_extensions)

    def test_link_allowed(self):
        urls = [
            Link('http://www.google.com/image'),
            Link('https://www.google.com/image'),
            Link('https://www.google.com/hello'),
            Link('https://www.amazon.com/something'),
            Link('https://www.google.com/music/some.mp3'),
            Link('https://www.google.com/doc/some.pdf'),
            Link('https://www.google.com/doc/some.ppt'),
        ]
        self.assertTrue(self.linkExtractor._link_allowed(urls[0]))
        self.assertTrue(self.linkExtractor._link_allowed(urls[1]))
        self.assertFalse(self.linkExtractor._link_allowed(urls[2]))
        self.assertFalse(self.linkExtractor._link_allowed(urls[3]))
        self.assertFalse(self.linkExtractor._link_allowed(urls[4]))
        self.assertFalse(self.linkExtractor._link_allowed(urls[5]))
        self.assertFalse(self.linkExtractor._link_allowed(urls[6]))

    def test_get_response_text(self):
        from urllib.request import urlopen
        response = urlopen('http://github.com/')
        result = self.linkExtractor._get_response_text(response, func_name='read')
        self.assertTrue(isinstance(result, str))

    def test_deduplicate(self):
        links = [
            Link('http://github.com/'),
            Link('http://github.com/'),
            Link('http://github.com/'),
            Link('http://google.com/'),
            Link('http://google.com/'),
            Link('http://google.com/')
        ]
        links = self.linkExtractor._deduplicate(links)
        self.assertEqual(len(links), 2)

    def test_iter_links(self):
        HTML = etree.HTML(self.response.text)
        els = []
        for el, attr, attr_val in self.linkExtractor._iter_links(HTML):
            els.append(el)
        self.assertEqual(len(els), 4)

    def test_process(self):
        links = self.linkExtractor._process(self.response)
        self.assertEqual(len(links), 4)

    def test_extract_links(self):
        links = self.linkExtractor.extract_links(self.response)
        self.assertEqual(len(links), 3)


if __name__ == '__main__':
    unittest.main()
