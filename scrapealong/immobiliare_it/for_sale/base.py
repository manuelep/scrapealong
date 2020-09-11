# -*- coding: utf-8 -*-

from . import scrape
from .. import settings
from ...fetch import fetch, SlowFetcher
from ...base import BasePicker
from ...helpers import Loop

import asyncio
from diskcache import Cache
from itertools import chain

init_semaphoro = asyncio.Semaphore(1)

async def get_or_call(key, func, expire=60):
    with Loop() as loop:
        async with init_semaphoro:
            with Cache(settings.CACHE_PATH, disk_pickle_protocol=3) as cache:
                try:
                    result = await loop.run_in_executor(None, cache.get, key)
                except ValueError:
                    result = None
                if result is None:
                    val = await func()
                    await loop.run_in_executor(None, cache.set, key, val, expire)
                    result = await loop.run_in_executor(None, cache.get, key)
    return result

async def get_macro_links():
    """ Returns dictionary like:
    {(<state>,<comune>,): <url>}
    """
    resp_provincie = await fetch(settings.BASE_URL)
    provincie = scrape.provincie(resp_provincie)

    async def foo(prov):
        resp = await fetch(prov['url'])
        return scrape.comuni(resp, prov['state'])

    res = await asyncio.gather(*[foo(pp) for pp in provincie])
    return dict(list(chain(*res)))

class MultiPicker(BasePicker):
    """docstring for MultiPicker."""

    LANG = 'en'

    def __init__(self):
        super(MultiPicker, self).__init__()

        with Loop() as loop:
            self.macro_links = loop.run_until_complete(
                get_or_call(
                    settings.BASE_URL,
                    get_macro_links,
                    expire = settings.EXPIRE
                )
            )

    # def url(self, page=None):
    #     """ """



        # parts = [self.prefix, self.code, self.suffix]
        # if not page is None:
        #     parts.insert(2, self.PAGINATION_PREFIX+format(page, '02d'))
        # path = '-'.join(parts)
        # return myurl(settings.BASE_URL, path)
