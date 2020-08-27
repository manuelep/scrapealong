# -*- coding: utf-8 -*-

from . import settings

import aiohttp
from bs4 import BeautifulSoup
import asyncio
import re

from pyppeteer import launch
from pyppeteer.errors import ElementHandleError
from pyppeteer.errors import TimeoutError

FETCH_TIMEOUT = 25.
BROWSE_TIMEOUT = 25000
RETRY_WITHIN = 10

async def fetch(url, retry=3):
    """ Fetches the given url and return the parsed page body
    DOC:
        * https://www.crummy.com/software/BeautifulSoup/bs4/doc/
    """
    timeout = aiohttp.ClientTimeout(total=FETCH_TIMEOUT)

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

async def browse(url, retry=3):

    info = {}

    browser = await launch()
    page = await browser.newPage()

    for tt in range(retry):
        try:
            res_ = await page.goto(url, timeout=BROWSE_TIMEOUT)
        except TimeoutError as err:
            if tt < retry-1:
                await asyncio.sleep(RETRY_WITHIN)
                continue
            else:
                print(url)
                raise err
        else:
            # body = await res_.text()
            body = await page.content()
            break

    try:
        span = await page.evaluate('''() => {
            var elem = document.querySelector('[data-test-target="staticMapSnapshot"]');
            return elem.outerHTML
        }''')
    except ElementHandleError:
        lon_lat = None
    else:
        center_ = re.search(';center=.*?\&', span)
        if not center_ is None:
            lon_lat = list(map(float, center_.group()[8:-1].split(',')))[::-1]
        else:
            lon_lat = None

    await browser.close()

    return lon_lat, BeautifulSoup(body, "html.parser")

class SlowFetcher(object):
    """docstring for SlowFetcher."""

    def __init__(self, QUEUE_LENGTH=settings.QUEUE_LENGTH):
        super(SlowFetcher, self).__init__()
        self.semaphoro = asyncio.Semaphore(QUEUE_LENGTH)

    async def fetch(self, url):
        async with self.semaphoro:
            response = await fetch(url)
        return response

    async def browse(self, url):
        async with self.semaphoro:
            response = await browse(url)
        return response
