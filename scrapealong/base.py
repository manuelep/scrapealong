# -*- coding: utf-8 -*-

from .helpers import Loop
from .common import logger

import asyncio
import aiohttp
from pyppeteer import launch
from bs4 import BeautifulSoup

FETCH_TIMEOUT = 25.
BROWSE_TIMEOUT = 25000
RETRY_WITHIN = 10

parser = lambda body: BeautifulSoup(body, "html.parser")

class ScrapeError(object):
    """docstring for ScrapeError."""

    def __init__(self, key, *args, **kw):
        super(ScrapeError, self).__init__(*args, **kw)
        self.key = key


class BasePicker(object):
    """docstring for BasePicker."""

    def __call__(self, *args, **kwargs):
        with Loop() as loop:
            res = loop.run_until_complete(self.run(*args, **kwargs))
        return res

    async def run(self):
        """ """
        raise NotImplementedError()

fetch_semaphoro = asyncio.Semaphore(10)
browse_semaphoro = asyncio.Semaphore(10)

class BaseBrowser(object):
    """docstring for BaseBrowser."""

    def __init__(self, url):
        super(BaseBrowser, self).__init__()
        self.url = url
        # self.lon_lat = None

    @staticmethod
    async def _page_callback(page):
        """  """
        raise NotImplementedError

    def __call__(self):
        """ """
        raise NotImplementedError

    def _load(self):
        """  """
        raise NotImplementedError

    async def _fetch(self, retry=3):
        """ Fetches the given url and return the parsed page body
        DOC:
            * https://www.crummy.com/software/BeautifulSoup/bs4/doc/
        """
        timeout = aiohttp.ClientTimeout(total=FETCH_TIMEOUT)

        async with aiohttp.ClientSession(timeout=timeout) as session:
            for tt in range(retry):
                async with fetch_semaphoro:
                    try:
                        async with session.get(self.url) as response:
                            body = await response.text()
                    except (aiohttp.ClientConnectorError, asyncio.TimeoutError) as err:
                        if tt < retry-1:
                            logger.warning(err)
                            logger.info(f"Fetch will be retryed within {RETRY_WITHIN} sec")
                            await asyncio.sleep(RETRY_WITHIN)
                            continue
                        else:
                            logger.error(err)
                            raise
                    else:
                        self.status = response.status
                        if response.status>=400:
                            return
                        break

        self._body = body
        self._load()

    async def _browse(self, retry=3):

        async with browse_semaphoro:
            browser = await launch()
            page = await browser.newPage()

            for tt in range(retry):
                try:
                    response = await page.goto(self.url, timeout=BROWSE_TIMEOUT)
                except TimeoutError as err:
                    if tt < retry-1:
                        logger.warning(err)
                        logger.info(f"Fetch will be retryed within {RETRY_WITHIN} sec")
                        await asyncio.sleep(RETRY_WITHIN)
                        continue
                    else:
                        logger.error(err)
                        raise
                else:
                    self.status = response.status
                    if response.status>=400:
                        return

                    break

            # body = await res_.text()
            body = await page.content()
            await self._page_callback(page)

            await browser.close()
        self._body = body
        self._load()

    @property
    def body(self):
        return parser(self._body)
