__all__ = ['Task']


class Task(object):
    """
    A Task class represent the task entity object in the life cycle of crawler,
    it's going to pass between Crawler and Engine.
    """

    __slots__ = [
        'url', 'parsed_data', 'exception',
        'redirect_num', 'retries_num', 'redirect_url',
        'response',
    ]

    def __init__(self, url,
                 parsed_data=None,
                 exception=None,
                 redirect_num=0,
                 retries_num=0,
                 redirect_url=None,
                 response=None):
        self.url = url
        self.parsed_data = parsed_data
        self.exception = exception
        self.redirect_num = redirect_num
        self.retries_num = retries_num
        self.redirect_url = redirect_url
        self.response = response

    def __repr__(self):
        return 'Task (redirect: %s, redirect url: %s, retries: %s, response: %s)' \
               % (
                   self.redirect_num, self.redirect_url,
                   self.retries_num, str(self.response)
               )

    __str__ = __repr__
