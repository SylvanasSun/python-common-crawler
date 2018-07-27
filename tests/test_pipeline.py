import unittest
from unittest.mock import patch, mock_open, MagicMock

from common_crawler.pipeline.file import SimpleFilePipeline
from common_crawler.task import Task
from tests.mock import FakedObject


class TestSimpleFilePipeline(unittest.TestCase):
    def setUp(self):
        self.open_path = 'builtins.open'
        url = 'https://www.example.com'

        response = FakedObject(url=url,
                               status=200,
                               charset='utf-8',
                               content_type=None,
                               content_length=None,
                               reason=None,
                               headers=None,
                               text=None)

        self.task = Task(url=url,
                         parsed_data='Text',
                         response=response)

    def test_transmit(self):
        m = mock_open()
        expected_mode = 'wb+'
        expected_encode = 'utf-8'

        with patch(self.open_path, m):
            with SimpleFilePipeline() as pipeline:
                pipeline.transmit(task=self.task, encode=expected_encode)

        domain = self.task.url[self.task.url.find('www'):]
        response = self.task.response
        default_filename = '%s:%s.html' % (domain, response.status)

        m.assert_called_once_with(default_filename, expected_mode)
        handle = m()
        handle.write.assert_called_once_with(self.task.parsed_data.encode(expected_encode))

    def test_suffix(self):
        m = mock_open()
        expected_suffix = 'txt'
        expected_mode = 'wb+'
        expected_encode = 'utf-8'

        with patch(self.open_path, m):
            with SimpleFilePipeline() as pipeline:
                pipeline.transmit(task=self.task, suffix=expected_suffix, encode=expected_encode)

        domain = self.task.url[self.task.url.find('www'):]
        response = self.task.response
        expected_filename = '%s:%s.%s' % (domain, response.status, expected_suffix)

        m.assert_called_once_with(expected_filename, expected_mode)
        handle = m()
        handle.write.assert_called_once_with(self.task.parsed_data.encode(expected_encode))

    def test_task_with_invalid(self):
        self.task = MagicMock(url='https://www.example.com',
                              parsed_data='Test',
                              status=200)

        with SimpleFilePipeline() as pipeline:
            with self.assertRaises(ValueError):
                pipeline.transmit(task=self.task)


if __name__ == '__main__':
    unittest.main()
