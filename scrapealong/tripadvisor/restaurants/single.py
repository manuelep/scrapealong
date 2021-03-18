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
        geo_and_props = await asyncio.gather(*[fetcher.browse(url) for url in tqdm(urls)])

        return map(lambda args: (args[0], scrape.details(*args[1:]), args[1],), geo_and_props)

class Browser(Browser_):
    """ """

    scrape = lambda self, response: scrape.details(response)
