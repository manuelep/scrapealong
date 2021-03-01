# -*- coding: utf-8 -*-

from .immobiliare_it.for_sale.single import Browser as ForSaleProp
from .helpers import Loop
import asyncio

async def fetch_from_immobiliare_(url):
    browser = ForSaleProp(url)
    await asyncio.gather(browser())
    return browser

def fetch_from_immobiliare(url):
    with Loop() as loop:
        updates = loop.run_until_complete(fetch_from_immobiliare_(url))
    return updates
