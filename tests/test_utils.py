import unittest

from common_crawler.utils.misc import *
from common_crawler.utils.url import *


class TestMisc(unittest.TestCase):
    """Test for common_crawler.utils.misc"""

    def test_dynamic_import(self):
        func_full_name = 'math.pow'
        class_full_name = 'queue.Queue'
        result = dynamic_import(func_full_name,
                                DynamicImportReturnType.FUNCTION,
                                2, 2)
        self.assertEqual(result, 4)
        q = dynamic_import(class_full_name, DynamicImportReturnType.CLASS)
        import queue
        self.assertTrue(isinstance(q, queue.Queue))

        p = dynamic_import('math.pi', DynamicImportReturnType.VARIABLE)
        from math import pi
        self.assertEqual(p, pi)

        with self.assertRaises(TypeError):
            dynamic_import(1000, DynamicImportReturnType.VARIABLE)
        with self.assertRaises(AttributeError):
            dynamic_import(class_full_name, 'FAKE')

    def test_verify_variable_type(self):
        s = 'hello'
        with self.assertRaises(TypeError):
            verify_variable_type(s, int, 'the type must be integer')
        verify_variable_type(s, str, 'the type must be string')

    def test_verify_configuration(self):
        config = {'hello': 'world'}
        self.assertTrue(verify_configuration(config))
        config = ['hello']
        self.assertFalse(verify_configuration(config))
        config = None
        self.assertFalse(verify_configuration(config))

    def test_matches(self):
        import re
        regexes = [re.compile('[ab]*abb'), re.compile('[cd]*cdd')]
        self.assertTrue(matches('abbbabb', regexes))
        self.assertTrue(matches('ddcdcdd', regexes))
        self.assertFalse(matches('hello', regexes))

    def test_arg_to_iter(self):
        arg = 'example'
        self.assertTrue(isinstance(arg_to_iter(arg), list))
        arg = None
        self.assertTrue(isinstance(arg_to_iter(arg), list))
        arg = ['example']
        self.assertTrue(isinstance(arg_to_iter(arg), list))

    def test_compile_regexes(self):
        import re
        RE_TYPE = type(re.compile('', 0))
        regexes = ['abb*', 'bb+a']
        regexes = compile_regexes(regexes)
        for r in regexes:
            self.assertTrue(isinstance(r, RE_TYPE))

    def test_unique_list(self):
        args = [1, 2, 3, 4, 5, 100, 100, 101, 101]
        args = unique_list(args)
        self.assertEqual(len(args), 7)


class TestUrl(unittest.TestCase):
    """Test for common_crawler.utils.url"""

    def test_is_valid_url(self):
        url = 'https://www.google.com/'
        self.assertTrue(is_valid_url(url))
        url = 'http://www.google.com/'
        self.assertTrue(is_valid_url(url))
        url = 'file://balabala'
        self.assertTrue(is_valid_url(url))
        url = 'cow://balabala'
        self.assertTrue(is_valid_url(url=url, valid_prefix={'cow'}))

    def test_parse_url(self):
        from urllib.parse import ParseResult
        url = 'https://www.quora.com/'
        result = parse_url(url)
        self.assertTrue(isinstance(result, ParseResult))
        self.assertTrue(isinstance(parse_url(result), ParseResult))

    def test_url_in_domains(self):
        url = 'https://www.quora.com/'
        domains = ['www.quora.com']
        self.assertTrue(url_in_domains(url, domains))
        self.assertFalse(url_in_domains(url, ['www.google.com']))

    def test_url_has_extension(self):
        url = 'https://www.quora.com/hello.mp3'
        url_2 = 'https://www.quora.com/world.pdf'
        extensions = ['.mp3']
        self.assertTrue(url_has_extension(url, extensions))
        self.assertFalse(url_has_extension(url_2, extensions))

    def test_join_url(self):
        base_url = 'https://www.quora.com'
        url = '/hello'
        expect = base_url + url
        self.assertEqual(join_url(url, base_url), expect)
        self.assertEqual(join_url(base_url, base_url), base_url)

    def test_revise_urls(self):
        roots = (
            'https://www.quora.com',
            'https://www.google.com',
            'http://www.python.org',
            'www.netflix.com',
            'github.com',
            'www.198.1.1.1.com'
        )
        revised = revise_urls(roots)
        self.assertEqual(len(revised), 4)
        self.assertTrue(roots[4] not in revised)
        self.assertTrue(roots[5] not in revised)


if __name__ == '__main__':
    unittest.main()
