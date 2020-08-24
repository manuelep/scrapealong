# -*- coding: utf-8 -*-

import asyncio
from diskcache import Cache

CACHE_PATH = '/tmp/'

async def get_or_call(key, func, expire=60):
    with Cache(CACHE_PATH, disk_pickle_protocol=3) as cache:
        loop = asyncio.get_event_loop()
        try:
            result = await loop.run_in_executor(None, cache.get, key)
        except ValueError:
            result = None
        if result is None:
            val = await func()
            await loop.run_in_executor(None, cache.set, key, val, expire)
            result = await loop.run_in_executor(None, cache.get, key)
        return result

class Loop(object):
    """docstring for Loop."""

    def __init__(self):
        super(Loop, self).__init__()
        if asyncio.get_event_loop().is_closed():
            self.loop = asyncio.new_event_loop()
        else:
            self.loop = asyncio.get_event_loop()

    def __enter__(self):
        """ """
        return self.loop

    def __exit__(self, exc_type, exc_value, traceback):
        """ """
        # self.loop.close()