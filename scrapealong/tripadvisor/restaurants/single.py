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
        geo_and_props = await asyncio.gather(*[fetcher.fetch(url) for url in tqdm(urls)])

        # return map(lambda args: (args[0], scrape.details(*args[1:]), args[1],), geo_and_props)
        return map(lambda pp: scrape.details(pp[0], pp[1]), zip(geo_and_props,urls))

class Browser(Browser_):

    def _load(self):
        self.sid, self.lon_lat, self.details, self.warnings = scrape.details(self.body,self.url)
