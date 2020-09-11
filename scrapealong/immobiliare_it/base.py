# -*- coding: utf-8 -*-

from ..base import BaseBrowser

class Browser(BaseBrowser):
    """docstring for Browser."""

    async def _page_callback(self, page):
        """  """

    __call__ = BaseBrowser._fetch

    # def load(self):
    #     self.details = scrape.details(self.body, self.url)
