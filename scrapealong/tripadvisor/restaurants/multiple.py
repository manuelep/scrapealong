# -*- coding: utf-8 -*-

from ...fetch import fetch, SlowFetcher
from . import scrape
from . import settings
from ..base import MultiPicker
from itertools import chain
from concurrent.futures._base import TimeoutError
import asyncio
from tqdm import tqdm

class Picker(MultiPicker):
    """docstring for Picker."""

    async def run(self):

        fetcher = SlowFetcher()

        response = await fetcher.fetch(self.url())

        offset = scrape.pagination(response)
        pages = [self.url(self.PAGINATE*ii) for ii in range(1,int(offset)+1)]

        first = [jj for jj in scrape.collection(response)]
        others_ = await asyncio.gather(*[fetcher.fetch(url_) for url_ in pages])

        return chain(first, *map(scrape.collection, tqdm(others_)))


if __name__ == '__main__':

    # url = myurl(settings.BASE_URL, settings.PATH_PREFIX, settings.TRACKED_LOCATIONS[0])
    picker = Picker(settings.TRACKED_LOCATIONS[0])
    res = picker()
    import pdb; pdb.set_trace()
