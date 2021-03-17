# -*- coding: utf-8 -*-

from . import settings

import aiohttp
from bs4 import BeautifulSoup
import asyncio
import re, json

# from pyppeteer import launch
# from pyppeteer.errors import ElementHandleError
# from pyppeteer.errors import TimeoutError
import logging
from kilimanjaro.timeformat import prettydelta
import datetime

FETCH_TIMEOUT = 25.
BROWSE_TIMEOUT = 25000
RETRY_WITHIN = 10

# create logger
logger = logging.getLogger(__name__)


ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

logger.addHandler(ch)

logger.setLevel(logging.DEBUG)

def timeit(func):
    async def wrapper(url, *args, **kwargs):
        assert asyncio.iscoroutinefunction(func)
        logger.info(f"Used method: {func.__name__}")
        logger.info(f"Calling url: {url}")
        start = datetime.datetime.now()
        result = await func(url, *args, **kwargs)
        end = datetime.datetime.now()
        elapsed = prettydelta(end-start)
        logger.info(elapsed)
        return result
    return wrapper

parser = lambda body: BeautifulSoup(body, "html.parser")

@timeit
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

    return parser(body)

# @timeit
# async def browse(url, retry=3):
#     """ DEPRECATED BUT STILL IN USE """

#     info = {}

#     browser = await launch()
#     page = await browser.newPage()

#     for tt in range(retry):
#         try:
#             res_ = await page.goto(url, timeout=BROWSE_TIMEOUT)
#         except TimeoutError as err:
#             if tt < retry-1:
#                 await asyncio.sleep(RETRY_WITHIN)
#                 continue
#             else:
#                 raise err
#         else:
#             # body = await res_.text()
#             body = await page.content()
#             break

#     try:
#         # This code get longitude and latitude information for *tripadvisor* pages only
#         span = await page.evaluate('''() => {
#             var elem = document.querySelector('[data-test-target="staticMapSnapshot"]');
#             return elem.outerHTML
#         }''')
#     except ElementHandleError:
#         lon_lat = None
#     else:
#         center_ = re.search(';center=.*?\&', span)
#         if not center_ is None:
#             lon_lat = list(map(float, center_.group()[8:-1].split(',')))[::-1]
#         else:
#             lon_lat = None

#     await browser.close()

#     return lon_lat, parser(body), url,

@timeit
async def browse_new(url, retry=3):
    """ DEPRECATED BUT STILL IN USE """
    timeout = aiohttp.ClientTimeout(total=FETCH_TIMEOUT)

    async with aiohttp.ClientSession(timeout=timeout) as session:
        for tt in range(retry):
            try:
                async with session.get(url) as response:
                    body = await response.text()
                    try:
                        response = BeautifulSoup(body, "html.parser")
                        columns = response.find('script', text = re.compile("""typeahead.recentHistoryList"""), attrs = {"type":"text/javascript"})
                        r1=re.findall(r"taStore\.store\('typeahead\.recentHistoryList'.*",str(columns))
                        r2=r1[0].replace("taStore.store('typeahead.recentHistoryList', ",'')
                        r2=r2[:-2]
                        ss=json.loads(r2)
                        coords=[]
                        [coords.append(x['coords']) for x in ss if "https://www.tripadvisor.com"+x['url']==link]
                        lon_lat=tuple(coords)
                    except ElementHandleError:
                        lon_lat = None
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

    return lon_lat, parser(body), url,

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
            # response = await browse(url)
            response = await browse_new(url)
        return response
