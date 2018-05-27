"""Some general purpose URL functions"""
import re
from posixpath import splitext
from urllib.parse import urlparse, ParseResult, urljoin, splitport

__all__ = [
    'is_valid_url', 'parse_url', 'url_in_domains', 'url_has_extension',
    'join_url', 'revise_urls', 'is_redirect', 'get_domain'
]

_DIGIT_HOST_REGEX = r'[\d\.]+'


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


def revise_urls(roots, strict=True):
    """
    Revise each URL which invalids in the specific roots and returns the list which revised.

    :param roots: a collection that contains urls
    :param strict: is it a strict matching
    """
    result = []

    for root in roots:
        if not root.startswith('http'):
            i = root.find('www')
            if i == -1: continue
            root = ('http://' + root[i:]).lower()
        parts = parse_url(root)
        host, port = splitport(parts.netloc)
        if not host:
            continue
        elif strict:
            host = host[4:]  # ignore prefix: www.
            if re.match(_DIGIT_HOST_REGEX, host):
                continue
        result.append(root)

    return result


def is_redirect(status):
    return status in (300, 301, 302, 303, 307)


def get_domain(url):
    """
    Get the domain from specified url for ignoring the prefix of HTTP/HTTPS

    e.g.:
        url = 'https://www.python.org/'
        get_domain(url) = 'www.python.org'
    """
    url = url[:url.rfind('/')] if url.rfind('/') != -1 else url
    return url[url.find('www'):] if url.find('www') != -1 else url
