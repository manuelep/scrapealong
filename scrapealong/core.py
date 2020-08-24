# -*- coding: utf-8 -*-

from .fetch import fetch
from .helpers import get_or_call, Loop

from itertools import chain
from concurrent.futures._base import TimeoutError
import asyncio

class Collector(object):
    """docstring for Collector2."""

    EXPIRE = 3600*24*7

    @timeLoggerDecorator()
    def __init__(self, url):
        """ Instantiate a new Collector object """
        super(Collector, self).__init__()
        self.url = url

        with Loop() as loop:

            self.macro_links = loop.run_until_complete(
                get_or_call(
                    self.url,
                    self.__get_macro_links,
                    expire = self.EXPIRE
                )
            )

    async def __get_macro_links(self):
        """
        """
        resp_provincie = await fetch(self.for_sale_url)
        provincie = scrap.provincie(resp_provincie)

        async def foo(prov):
            resp = await fetch(prov['url'])
            return scrap.comuni(resp, prov['state'])

        res = await asyncio.gather(*[foo(pp) for pp in provincie])
        return dict(list(chain(*res)))

    async def run(self, *locations):
        """ """

        semaphoro = asyncio.Semaphore(10)

        async def fetch_slowly(url, state, city):
            async with semaphoro:
                resp = await fetch(url)

            return  scrap.properties(resp, state=state, city=city)

        async def digg(comune_url, state, comune):
            """ Downloads property preliminary data """
            async with semaphoro:
                resp = await fetch(comune_url)

            pages = scrap.prop_pages(resp)

            preliminary_infos_0 = [jj for jj in scrap.properties(resp, city=comune, state=state)]
            # preliminary_infos_0 = map(lambda jj: dict(jj, city=comune, state=state), scrap.properties(resp))
            foo = await asyncio.gather(*[fetch_slowly(comune_url+'?pag={}'.format(pp), city=comune, state=state) for pp in range(2, pages+1)])
            preliminary_infos = chain(preliminary_infos_0, *foo)

            return preliminary_infos

        res = await asyncio.gather(*[digg(uu, *cc) for cc,uu in self.macro_links.items() if locations and (cc[1] in locations)])
        return chain(*res)
