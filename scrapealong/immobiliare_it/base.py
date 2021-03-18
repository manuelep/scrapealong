# -*- coding: utf-8 -*-

from ..base import BaseBrowser


class Browser(BaseBrowser):
    """docstring for Browser."""

    __call__ = BaseBrowser._fetch

    @staticmethod
    def scrape():
        raise NotImplementedError()

    def _load(self):

        self.sid, self.lon_lat, self.details, self.warnings = self.scrape(self.body)
