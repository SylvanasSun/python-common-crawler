from lxml import etree

from common_crawler.link import Link
from common_crawler.link_extractor import LinkExtractor, HTML5_WHITESPACE
from common_crawler.utils.url import join_url

__all__ = ['LxmlLinkExtractor']

_LXML_STRING_CONTENT = etree.XPath('string()')


class LxmlLinkExtractor(LinkExtractor):
    """
    The class LxmlLinkExtractor is an implementation of LinkExtractor base on
    lxml and it follows the behavior of LinkExtractor that is extractor links
    from the response and filtering invalid link according to specific rules.
    """

    def __init__(self, **kwargs):
        """The parameter specification see the superclass LinkExtractor."""
        super(LxmlLinkExtractor, self).__init__(**kwargs)

    def _process(self, response, encoding='utf-8'):
        base_url = response.url
        root = etree.HTML(self._get_response_text(response))

        if self.restrict_xpaths:
            docs = []
            for x in self.restrict_xpaths:
                docs.extend(root.xpath(x))
        else:
            docs = [root]

        all_links = []
        for doc in docs:
            links = self._extract(doc, base_url, encoding)
            all_links.extend(links)

        return all_links

    def _extract(self, selector, base_url, encoding):
        """The specification see the superclass LinkExtractor."""
        links = []

        for el, attr, attr_val in self._iter_links(selector):
            try:
                if self.strip:
                    attr_val = attr_val.strip(HTML5_WHITESPACE)
                attr_val = join_url(url=attr_val, base_url=base_url)
            except ValueError:
                continue
            else:
                url = self.process_attr(attr_val)
                if url is None:
                    continue

            url = url.decode(encoding) if isinstance(url, bytes) else url
            # fix relative link after process_attr
            url = join_url(url=url, base_url=base_url)
            link = Link(url=url, text=_LXML_STRING_CONTENT(el) or u'')
            links.append(link)

        return links

    def _iter_links(self, document):
        """Iterate elements of the document by lxml.etree"""
        for element in document.iter(etree.Element):
            if not self.scan_tag_func(element.tag):
                continue
            attribs = element.attrib
            for attrib in attribs:
                if not self.scan_attr_func(attrib):
                    continue
                yield (element, attrib, attribs[attrib])
