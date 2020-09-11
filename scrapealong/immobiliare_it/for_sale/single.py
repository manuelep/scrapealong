# -*- coding: utf-8 -*-

from ...fetch import SlowFetcher
from . import scrape
from ...base import BasePicker
from ..base import Browser as Browser_

import asyncio
from tqdm import tqdm

class Picker(BasePicker):
    """docstring for Picker."""

    async def run(self, urls):
        fetcher = SlowFetcher()
        resps = await asyncio.gather(*[fetcher.fetch(url) for url in tqdm(urls)])
        return map(scrape.property, resps)

class Browser(Browser_):
    """docstring for Browser."""

    def _load(self):
        self.sid, self.lon_lat, self.details, self.warnings = scrape.details(self.body)
