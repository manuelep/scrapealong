# -*- coding: utf-8 -*-

from ...fetch import SlowFetcher
from . import scrape
from . import settings
from ..base import BasePicker
# from itertools import chain
# from concurrent.futures._base import TimeoutError
import asyncio
from tqdm import tqdm
import re

# from pyppeteer.errors import ElementHandleError

# def loopOurls(urls):
#     for url in tqdm(urls):
#         try:
#             yield fetcher.browse(url)
#         except ElementHandleError:
#             pass

class Picker(BasePicker):
    """docstring for Picker."""

    async def run(self, urls):
        fetcher = SlowFetcher()
        geo_and_props = await asyncio.gather(*[fetcher.browse(url) for url in tqdm(urls)])

        return map(lambda args: (args[0], scrape.details(args[1]),), geo_and_props)
