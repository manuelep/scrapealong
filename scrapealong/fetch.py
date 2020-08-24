# -*- coding: utf-8 -*-

from . import settings

import aiohttp
from bs4 import BeautifulSoup
import asyncio

TIMEOUT = 25.
RETRY_WITHIN = 5

async def fetch(url, retry=3):
    """ Fetches the given url and return the parsed page body
    DOC:
        * https://www.crummy.com/software/BeautifulSoup/bs4/doc/
    """
    timeout = aiohttp.ClientTimeout(total=TIMEOUT)

    async with aiohttp.ClientSession(timeout=timeout) as session:
        for tt in range(retry):
            try:
                async with session.get(url) as response:
                    body = await response.text()
            except (aiohttp.ClientConnectorError, asyncio.TimeoutError) as err:
                if tt < retry-1:
                    await asyncio.sleep(RETRY_WITHIN)
                    continue
                else:
                    raise
            else:
                if response.status>=400:
                    return
                break

    return BeautifulSoup(body, "html.parser")

class SlowFetcher(object):
    """docstring for SlowFetcher."""

    def __init__(self, QUEUE_LENGTH=settings.QUEUE_LENGTH):
        super(SlowFetcher, self).__init__()
        self.semaphoro = asyncio.Semaphore(QUEUE_LENGTH)

    async def fetch(self, url):
        async with self.semaphoro:
            response = await fetch(url)
        return response
