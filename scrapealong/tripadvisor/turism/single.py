# -*- coding: utf-8 -*-

# from ...fetch import SlowFetcher
from . import scrape
# from ..base import BasePicker
from ..base import Browser as Browser_

# import asyncio
# from tqdm import tqdm

# class Picker(BasePicker):
#     """docstring for Picker."""
#
#     async def run(self, urls):
#         fetcher = SlowFetcher()
#         responses = await asyncio.gather(*[fetcher.fetch(url) for url in tqdm(urls)])
#
#         return map(lambda args: (args[0], scrape.details(*args[1:]), args[1],), geo_and_props)

class Browser(Browser_):
    """ """

    scrape = lambda self, response: scrape.details(response)

# if __name__ == '__main__':
#     bb = Browser('https://www.tripadvisor.com/Attraction_Review-g187849-d23214758-Reviews-Via_Riccardo_Galeazzi-Milan_Lombardy.html')
