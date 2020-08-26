# -*- coding: utf-8 -*-

from .. import settings
from ..helpers import Loop, myurl

class BasePicker(object):
    """docstring for BasePicker."""

    def __call__(self, *args, **kwargs):
        with Loop() as loop:
            res = loop.run_until_complete(self.run(*args, **kwargs))
        return res

    async def run(self):
        """ """
        raise NotImplementedError()


class MultiPicker(BasePicker):
    """docstring for MultiPicker."""

    PAGINATE = settings.PAGINATE
    PAGINATION_PREFIX = settings.PAGINATION_PREFIX

    def __init__(self, main_path):
        super(MultiPicker, self).__init__()
        self.prefix, self.code, self.suffix = self.__urlparse(main_path)

    @staticmethod
    def __urlparse(path):
        parts = path.split('-')
        return parts[0], parts[1], '-'.join(parts[2:])

    def url(self, ii=None):
        parts = [self.prefix, self.code, self.suffix]
        if not ii is None:
            parts.insert(2, self.PAGINATION_PREFIX+format(ii, '02d'))
        path = '-'.join(parts)
        return myurl(settings.BASE_URL, path)
