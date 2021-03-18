# -*- coding: utf-8 -*-

from .helpers import Loop
from .common import logger

import asyncio
import aiohttp
from pyppeteer import launch
import pyppeteer.errors
from bs4 import BeautifulSoup
import traceback

FETCH_TIMEOUT = 25.
BROWSE_TIMEOUT = 25000
RETRY_WITHIN = 5

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
browse_semaphoro = asyncio.Semaphore(1)

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

    async def _fetch(self, retry=5):
        """ Fetches the given url and return the parsed page body
        DOC:
            * https://www.crummy.com/software/BeautifulSoup/bs4/doc/
        """
        timeout = aiohttp.ClientTimeout(total=FETCH_TIMEOUT)

        async with aiohttp.ClientSession(timeout=timeout) as session:
            for tt in range(1, retry+1):
                async with fetch_semaphoro:
                    try:
                        async with session.get(self.url) as response:
                            body = await response.text()
                    except (aiohttp.ClientConnectorError, asyncio.TimeoutError) as err:
                        if tt < retry:
                            logger.warning(err)
                            logger.info(f"Attempt {tt} failed. Fetch will be retryed within {RETRY_WITHIN} sec")
                            logger.info(self.url)
                            await asyncio.sleep(RETRY_WITHIN)
                            continue
                        else:
                            logger.warning(f"Attempt {tt} failed")
                            logger.error(err)
                            raise
                    else:
                        self.status = response.status
                        if response.status>=400:
                            return
                        break

        self._body = body
        self._load()

    async def _browse(self, retry=5):

        async with browse_semaphoro:

            for tt in range(1, retry+1):
                try:
                    browser = await launch()
                    page = await browser.newPage()
                    response = await page.goto(self.url, timeout=BROWSE_TIMEOUT)
                except pyppeteer.errors.TimeoutError as err:
                    if tt < retry:
                        logger.warning(err)
                        logger.info(f"Attempt {tt} failed. Fetch will be retryed within {RETRY_WITHIN} sec")
                        logger.info(self.url)
                        await asyncio.sleep(RETRY_WITHIN)
                        await page.close()
                        await browser.close()
                        continue
                    else:
                        logger.warning(f"Attempt {tt} failed")
                        logger.error(err)
                        await page.close()
                        await browser.close()
                        break
                        # raise
                except pyppeteer.errors.BrowserError as err:
                    logger.critical(err)
                    logger.error(traceback.format_exc())
                    continue
                except pyppeteer.errors.PageError as err:
                    logger.critical(err)
                    logger.error(traceback.format_exc())
                    continue
                else:
                    self.status = response.status
                    if response.status>=400:
                        return
                    else:
                        await self._page_callback(page)
                    self._body = await page.content()
                    await page.close()
                    await browser.close()
                    self._load()
                    break

    @property
    def body(self):
        return parser(self._body)
