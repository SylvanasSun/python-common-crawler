"""Global configuration file represented in python code."""

__all__ = ['CONFIGURATION', 'COMPONENTS_CONFIG']

CONFIGURATION = {
    # The name of the crawler
    'name': 'common_crawler',

    # Root urls, it is the starting point of the crawler
    'roots': (),

    # A tuple(or single value) of a string containing domains which won't be considered for extracting the links.
    'deny_domains': (),

    # A tuple(or single value) of a string containing domains which will be considered for extracting the links.
    'allow_domains': (),

    # Strict host matching
    'strict': True,

    # If the flag is true, crawl along the link until can't extract any no crawled links
    # else just crawl links of the around
    'follow': True,

    # The tuple of the regex rule for link that allowed to extract in the LinkExtractor
    'allowed_rule': (),

    # The tuple of the regex rule for link that denied to extract in the LinkExtractor
    'denied_rule': (),

    # Log level, from 0 to 3: ERROR, WARNING, INFO, DEBUG
    'log_level': 2,

    # The path of the log output file and default is not output to the file
    'log_filename': None,

    # The output format of the log
    'log_format': '%(asctime)s:%(levelname)s:%(message)s',

    # The function used to initialize the log and it can be a fully qualified string
    # can also be set to a function object, the config item has precedence over log_level and log_file
    'log_init_fn': 'common_crawler.engines._init_logging',

    # Limit the maximum number of redirect chains, if it's a negative number represent unlimited
    # The unlimited pattern will not limit the number of redirects this could lead to infinite redirection
    'max_redirect': 10,

    # Limit the maximum number of retries on network error
    'max_retries': 4,

    # Limit the maximum number of concurrent connections
    'max_tasks': 100,

    # The interval is a time that crawls interval (unit seconds)
    'interval': 1
}

# Specify the address of each component
COMPONENTS_CONFIG = {
    # The crawler is for crawling url then return an object FetchedUrl to Engine
    # for extract link and handle data, the class must be a subclass of common_crawler.crawler.Crawler
    'crawler': 'common_crawler.crawler.async.AsyncCrawler',

    # The link_extractor is for extract link from a specified response and it must be a subclass
    # of common_crawler.link_extractor.LinkExtractor, about rules of this action, is set in the
    # CONFIGURATION such as deny_domains, allow_domains and so on
    'link_extractor': 'common_crawler.link_extractor.lxml.LxmlLinkExtractor',

    # The pipeline is for transmitting parsed data to a place that you want it and must be a subclass of
    # common_crawler.pipeline.Pipeline
    'pipeline': 'common_crawler.pipeline.file.SimpleFilePipeline'
}
