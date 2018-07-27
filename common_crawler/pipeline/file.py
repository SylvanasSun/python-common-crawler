import multiprocessing
import os
from concurrent.futures import ThreadPoolExecutor

from common_crawler.pipeline import Pipeline
from common_crawler.utils.url import get_domain

__all__ = ['SimpleFilePipeline']


class SimpleFilePipeline(Pipeline):
    """
    Transmit the parsed data to the file simply,
    built-in a thread pool for increase efficiency.

    notice, this class must manually call close() for release resource!!!
    """

    def __init__(self,
                 enable_multithread=True,
                 max_workers=multiprocessing.cpu_count(),
                 thread_name_prefix='SimpleFilePipeline-',
                 **kwargs):
        super(__class__, self).__init__(**kwargs)

        self.enable_multithread = enable_multithread
        if enable_multithread:
            self.threadpool = ThreadPoolExecutor(max_workers=max_workers,
                                                 thread_name_prefix=thread_name_prefix)

    def transmit(self,
                 task,
                 suffix='html',
                 dirname='',
                 encode='utf-8',
                 **kwargs):
        """
        Overwrite this function for avoiding call close() when each time perform
        transmit(), because close() will release resource of the thread pool and
        will cause subsequent operation is disabled
        """
        super(__class__, self)._init_task(task)

        self.setup(**kwargs)

        filename = '%s:%s.%s' % (get_domain(self.task.url),
                                 self.task.response.status,
                                 suffix)
        if dirname:
            if not os.path.exists(dirname):
                os.makedirs(dirname)
            filename = os.path.join(dirname, filename)

        self.handle(filename, encode)

    def setup(self, **kwargs):
        pass

    def handle(self, filename, encode):
        if self.enable_multithread:
            self.threadpool.submit(self._work, filename, encode)
        else:
            self._work(filename, encode)

    def _work(self, filename, encode):
        with open(filename, 'wb+') as f:
            f.write(self.data.encode(encode))

    def close(self, **kwargs):
        if self.enable_multithread:
            self.threadpool.shutdown()
