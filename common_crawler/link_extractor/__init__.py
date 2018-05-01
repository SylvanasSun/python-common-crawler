"""The link extractor extracts the link according to the specified rule"""

from abc import ABC, abstractmethod

from w3lib.url import canonicalize_url

from common_crawler.utils.misc import arg_to_iter, compile_regexes, matches, unique_list
from common_crawler.utils.url import is_valid_url, url_in_domains, url_has_extension, parse_url

__all__ = ['LinkExtractor', 'IGNORED_EXTENSIONS', 'HTML5_WHITESPACE']

# The list  of the file extensions and not followed if they occur in links
IGNORED_EXTENSIONS = [
    # images
    'mng', 'pct', 'bmp', 'gif', 'jpg', 'jpeg', 'png', 'pst', 'psp', 'tif',
    'tiff', 'ai', 'drw', 'dxf', 'eps', 'ps', 'svg',

    # audio
    'mp3', 'wma', 'ogg', 'wav', 'ra', 'aac', 'mid', 'au', 'aiff',

    # video
    '3gp', 'asf', 'asx', 'avi', 'mov', 'mp4', 'mpg', 'qt', 'rm', 'swf', 'wmv',
    'm4a',

    # office suites
    'xls', 'xlsx', 'ppt', 'pptx', 'pps', 'doc', 'docx', 'odt', 'ods', 'odg',
    'odp',

    # other
    'css', 'pdf', 'exe', 'bin', 'rss', 'zip', 'rar',
]

HTML5_WHITESPACE = ' \t\n\r\x0c'


class LinkExtractor(ABC):
    """
    The abstract class LinkExtractor defines the behavior that extracts links from the specific
    response and the must follow the specific rules, each subclass must implement function _process()
    which represent the extract links logic.

    Each element in the extracted links must be an object Link from common_crawler.link.
    """

    def __init__(self, allow=(), deny=(), allow_domains=(), deny_domains=(),
                 tags=('a', 'area'), attrs=('href',), canonicalize=False, unique=True,
                 process_attr=None, deny_extensions=None, strip=True):
        """
        :param allow:
            a regular expression tuple(or single value) that the URLs must match in order to extract.
        :param deny:
            a regular expression tuple(or single value), the match the successful URLs will not be extracted.
        :param allow_domains:
            a tuple(or single value) of a string containing domains which will be considered for extracting the links.
        :param deny_domains:
            a tuple(or single value) of a string containing domains which won't be considered for extracting the links.
        :param tags:
            a tags list(or single value) to consider when extracting links.
        :param attrs:
            an attribute list(or single value) which should be considered when looking for links to extract, only for those tags specified in the tags param.
        :param canonicalize:
            canonicalize each extracted url (using w3lib.url.canonicalize_url).
        :param unique:
            whether duplicate filtering should be applied to extracted links.
        :param process_attr:
            a function which receives each value extracted from the tag and attributes scanned and can modify the value and return a new one.
        :param deny_extensions:
            a extension list(or single value) that should be ignored when extracting links.
        :param strip:
            whether to strip whitespaces from extracted attributes, according to HTML5 standard.
        """

        self.unique = unique
        self.strip = strip

        self.allowed_rule = compile_regexes(arg_to_iter(allow))
        self.denied_rule = compile_regexes(arg_to_iter(deny))
        self.allow_domains = set(arg_to_iter(allow_domains))
        self.deny_domains = set(arg_to_iter(deny_domains))

        self.deny_extensions = deny_extensions or IGNORED_EXTENSIONS
        self.deny_extensions = {'.' + x for x in arg_to_iter(deny_extensions)}

        tags, attrs = set(arg_to_iter(tags)), set(arg_to_iter(attrs))
        self.scan_tag_func, self.scan_attr_func = lambda x: x in tags, lambda x: x in attrs
        self.process_attr = process_attr if callable(process_attr) else lambda v: v

        self.canonicalize = canonicalize
        if canonicalize:
            self.link_key = lambda link: link.url
        else:
            self.link_key = lambda link: canonicalize_url(link.url,
                                                          keep_fragments=True)

    def _link_allowed(self, link):
        """Return true if the link meets the requirements of the rules."""
        if not is_valid_url(link.url):
            return False
        if self.allowed_rule and not matches(link.url, self.allowed_rule):
            return False
        if self.denied_rule and matches(link.url, self.denied_rule):
            return False
        parsed_url = parse_url(link.url)
        if self.allow_domains and not url_in_domains(parsed_url, self.allow_domains):
            return False
        if self.deny_domains and url_in_domains(parsed_url, self.deny_domains):
            return False
        if self.deny_extensions and url_has_extension(parsed_url, self.deny_extensions):
            return False
        return True

    def _get_response_text(self, response, func_name='text', encoding='utf-8'):
        """
        Return a text of the response by invoking the specific function,
        return itself if the response is the string.
        """
        if isinstance(response, str):
            return response
        if hasattr(response, func_name):
            text = getattr(response, func_name)
            text = text() if callable(text) else text
            return text.decode(encoding) if isinstance(text, bytes) else text
        raise ValueError('The response must be str or has a function or param for getting the text')

    def _deduplicate(self, links):
        """Remove duplicate links."""
        if self.unique:
            return unique_list(list_=links, key=self.link_key)
        return links

    def extract_links(self, response, encoding='utf-8'):
        """
        Return extracted links from the specific response according to rules,
        invoke the function _link_allowed() for filtering invalid links.
        """
        links = self._process(response, encoding)
        links = [x for x in links if self._link_allowed(x)]
        if self.canonicalize:
            for link in links:
                link.url = canonicalize_url(link.url)
        links = self._deduplicate(links)
        return links

    @abstractmethod
    def _process(self, response, encoding='utf-8'):
        """
        Specific extract link logic that subclass implementation,
        need basis on the params tags, attrs, process_attr and strip to extracts.
        """
        raise NotImplementedError
