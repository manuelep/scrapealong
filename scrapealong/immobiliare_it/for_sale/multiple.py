# -*- coding: utf-8 -*-

from .base import MultiPicker
from . import scrape
from ...fetch import fetch, SlowFetcher

import asyncio
from tqdm import tqdm
from itertools import chain

props = lambda resp, state, comune: dict(scrape.properties(resp), state=state, comune=comune)

class Digger(SlowFetcher):
    """docstring for Digger."""

    def __init__(self, QUEUE_LENGTH=10):
        super(Digger, self).__init__(QUEUE_LENGTH=QUEUE_LENGTH)

    async def digg(self, comune_url, comune, state):
        """ Downloads property preliminary data """
        first_page = await self.fetch(comune_url)
        npages = scrape.prop_pages(first_page)

        # preliminary_infos_0 = [jj for jj in scrape.properties(resp)]

        other_pages = await asyncio.gather(*[self.fetch(comune_url+'?pag={}'.format(pp)) for pp in range(2, npages+1)])
        # other_preliminary_infos = map(lambda resp: props(resp, state=state, comune=comune), other_pages)
        all_pages = chain((first_page,), other_pages)
        print(comune_url)
        return chain(*map(scrape.properties, all_pages))


class Picker(MultiPicker):
    """docstring for Picker."""

    async def run(self, *locations):

        fetcher = Digger()

        async def foo(cc):
            state, comune = cc[0]
            url = cc[1]
            info = await fetcher.digg(url, comune, state)
            return info

        res = await asyncio.gather(*list(map(
            foo,
            filter(
                lambda cc: (len(locations)>0 and (cc[0][1] in locations)),
                tqdm(self.macro_links.items(), desc="Downloading infos from sumary pages")
            )
        )))

        return chain(*res)
