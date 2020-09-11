# -*- coding: utf-8 -*-

from .import settings
from ..helpers import myurl
from ..base import BasePicker, BaseBrowser
from pyppeteer.element_handle import ElementHandleError
import re

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

    def url(self, page=None):
        parts = [self.prefix, self.code, self.suffix]
        if not page is None:
            parts.insert(2, self.PAGINATION_PREFIX+format(page, '02d'))
        path = '-'.join(parts)
        return myurl(settings.BASE_URL, path)


class Browser(BaseBrowser):
    """docstring for Browser."""

    __call__ = BaseBrowser._browse

    async def _page_callback(self, page):
        """  """
        try:
            # This code get longitude and latitude information for *tripadvisor* pages only
            span = await page.evaluate('''() => {
                var elem = document.querySelector('[data-test-target="staticMapSnapshot"]');
                return elem.outerHTML
            }''')
        except ElementHandleError:
            lon_lat = None
        else:
            center_ = re.search(';center=.*?\&', span)
            if not center_ is None:
                lon_lat = list(map(float, center_.group()[8:-1].split(',')))[::-1]
            else:
                lon_lat = None

        self.lon_lat = lon_lat
