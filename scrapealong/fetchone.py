# -*- coding: utf-8 -*-

from .immobiliare_it.for_sale.single import Browser as ForSaleProp
from .tripadvisor.hotels.single import Browser as HotelProp

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

# async def fetch_from_tripadvisor_hotels_(url):
#     browser = HotelProp(url)
#     await asyncio.gather(browser())
#     return browser
#
# def fetch_from_tripadvisor_hotels(url):
#     with Loop() as loop:
#         updates = loop.run_until_complete(fetch_from_tripadvisor_hotels_(url))
#     return updates

class fetchFromTripadvisorHotels(object):

    @staticmethod
    async def run(url):
        browser = HotelProp(url)
        await asyncio.gather(browser())
        return browser

    def __call__(self, url):
        with Loop() as loop:
            updates = loop.run_until_complete(self.run(url))
        return updates

fetch_from_tripadvisor_hotels = fetchFromTripadvisorHotels()


if __name__ == '__main__':

    res = fetch_from_tripadvisor_hotels('https://www.tripadvisor.com/Hotel_Review-g187826-d238197-Reviews-Best_Western_Hotel_Tigullio_Royal-Rapallo_Italian_Riviera_Liguria.html')

    import pdb; pdb.set_trace()
