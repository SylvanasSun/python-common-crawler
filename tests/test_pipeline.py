import unittest
from unittest.mock import patch, mock_open, MagicMock

from common_crawler.crawler import FetchedUrl
from common_crawler.pipeline.file import SimpleFilePipeline


class TestSimpleFilePipeline(unittest.TestCase):
    def setUp(self):
        self.open_path = 'builtins.open'
        self.task = FetchedUrl(url='https://www.example.com',
                               parsed_data='Test',
                               status=200,
                               charset='utf-8',
                               content_type=None,
                               content_length=None,
                               reason=None,
                               headers=None,
                               exception=None,
                               redirect_num=0,
                               retries_num=0,
                               redirect_url=None)

    def test_transmit(self):
        m = mock_open()
        expected_mode = 'wb+'
        expected_encode = 'utf-8'

        with patch(self.open_path, m):
            with SimpleFilePipeline() as pipeline:
                pipeline.transmit(task=self.task, encode=expected_encode)

        domain = self.task.url[self.task.url.find('www'):]
        default_filename = '%s:%s' % (domain, self.task.status)

        m.assert_called_once_with(default_filename, expected_mode)
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
