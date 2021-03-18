# -*- coding: utf-8 -*-

from ...fetch import fetch, SlowFetcher
from ..base import MultiPicker
from . import scrape, settings

from itertools import chain
# from concurrent.futures._base import TimeoutError
import asyncio
from tqdm import tqdm
from ...helpers import myurl

class Picker(MultiPicker):
    """docstring for Picker."""

    def url(self, page=None):
        parts = [self.prefix, self.code, self.suffix]
        if not page is None:
            parts[2] = parts[2].replace('a_allAttractions.true', self.PAGINATION_PREFIX+format(page, '02d'))
            # parts.insert(2, self.PAGINATION_PREFIX+format(page, '02d'))
        path = '-'.join(parts)
        return myurl(settings.BASE_URL, path)

    async def run(self):

        fetcher = SlowFetcher()

        first_page_url = self.url()
        response = await fetcher.fetch(first_page_url)

        offset = scrape.pagination(response)

        first = [jj for jj in scrape.collection(response)]

        if not offset is None:
            pages = [self.url(self.PAGINATE*ii) for ii in range(1,int(offset)+1)]
            others_ = await asyncio.gather(*[fetcher.fetch(url_) for url_ in pages])
        else:
            others_ = []

        return chain(first, *map(scrape.collection, tqdm(filter(None, others_))))


if __name__ == '__main__':

    from . import settings

    # from py4web.core import dumps
    # url = myurl(settings.BASE_URL, settings.PATH_PREFIX, settings.TRACKED_LOCATIONS[0])
    picker = Picker(settings.TRACKED_LOCATIONS[0])
    res = picker()
    import pdb; pdb.set_trace()
