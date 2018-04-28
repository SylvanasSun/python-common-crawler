"""Some general purpose URL functions"""
from posixpath import splitext
from urllib.parse import urlparse, ParseResult, urljoin

__all__ = [
    'is_valid_url', 'parse_url', 'url_in_domains', 'url_has_extension',
    'join_url'
]


def is_valid_url(url, valid_prefix={'http', 'https', 'file'}):
    return url.split('://', 1)[0] in valid_prefix


def parse_url(url, encoding='utf-8'):
    if isinstance(url, ParseResult):
        return url
    return urlparse(url, encoding)


def url_in_domains(url, domains):
    """Return true if the URL is in the specific domains"""
    host = parse_url(url).netloc.lower()
    if not host:
        return False
    domains = [d.lower() for d in domains]
    return any((host == d) or (host.endswith('.%s' % d)) for d in domains)


def url_has_extension(url, extensions):
    """Return true if the extension name of the URL path is in the specific extensions"""
    return splitext(parse_url(url).path)[1].lower() in extensions


def join_url(url, base_url, prefixes=('#', '/')):
    """
     Join a base URL and a possibly relative URL to form an absolute interpretation of the latter,
     return unmodified URL if it does not start with prefixes.
    """
    if url[0:1] in prefixes and len(url) > 1:
        return urljoin(base_url, url)
    else:
        return url
