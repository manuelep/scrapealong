# -*- coding: utf-8 -*-

from .for_sale.single import Browser

from ..helpers import Loop
import asyncio

async def __fetch(url):
    browser = Browser(url)
    await asyncio.gather(browser())
    return browser

def fetch(url):
    with Loop() as loop:
        updates = loop.run_until_complete(__fetch(url))
    return updates

if __name__ == '__main__':

    res = fetch('https://www.immobiliare.it/annunci/85791032/')

    import pdb; pdb.set_trace()
