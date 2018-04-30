import unittest

from common_crawler.utils.misc import *


class TestMisc(unittest.TestCase):
    """Test for common_crawler.utils.misc"""

    def test_dynamic_import(self):
        func_full_name = 'math.pow'
        class_full_name = 'queue.Queue'
        result = dynamic_import(func_full_name, 2, 2)
        self.assertEqual(result, 4)
        q = dynamic_import(class_full_name)
        import queue
        self.assertTrue(isinstance(q, queue.Queue))
        with self.assertRaises(TypeError):
            dynamic_import(1000)

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


if __name__ == '__main__':
    unittest.main()
