# -*- coding: utf-8 -*-

from .models import db

from . import settings

from .tripadvisor.fetchall import fetchall_ as fetchall_ta
# from .tripadvisor.settings import SOURCE_NAME as tripadvisor

from .immobiliare_it.fetchall import fetchall_ as fetchall_im
# from .immobiliare_it.settings import SOURCE_NAME as immobiliare

from contextlib import contextmanager

from .tripadvisor.restaurants.single import Picker as ResPicker
from .tripadvisor.hotels.single import Picker as HotPicker
from .immobiliare_it.for_sale.single import Picker as SalPicker

from .tripadvisor.restaurants.scrape import details as res_details
from .tripadvisor.hotels.scrape import details as hot_details

from .immobiliare_it.for_sale.scrape import details as sal_details

from .tripadvisor.restaurants.single import Browser as Restaurant
from .tripadvisor.restaurants.scrape import AMENITY as RESTAURANT
from .tripadvisor.hotels.single import Browser as Hotel
from .tripadvisor.hotels.scrape import AMENITY as HOTEL
from .tripadvisor.tourism.single import Browser as Tourism
from .tripadvisor.tourism.scrape import AMENITY as TOURISM
from .immobiliare_it.for_sale.single import Browser as ForSaleProp
from .immobiliare_it.for_sale.scrape import AMENITY as FORSALE

from .fetch import parser
from .fetch import SlowFetcher

from .helpers import Loop

from geojson import Feature, Point
import asyncio
from tqdm import tqdm

def loopOdata(escape=True):

    for source_name, collection in [
        (settings.tripadvisor, fetchall_ta,),
        (settings.immobiliareit, fetchall_im,)
    ]:
        for amenity in collection():
            if not escape or db.amenity(
                sid = amenity['sid'],
                source_name = source_name
            ) is None:
                yield source_name, amenity

def populate(commit=False):
    """ Populates the local temporary database with raw informations from summary
    pages.
    """
    for source_name, updates in loopOdata(escape=True):
        new_id = db.amenity.insert(
            source_name = source_name,
            properties = updates
        )
    # import pdb; pdb.set_trace()
    if commit:
        db.commit()

def get_feature_(row, updates, lon_lat):

    assert row['sid']==updates['sid'], f"{row.sid} != {updates['sid']}"

    # TODO: In case lon_lat is None we could think to geocode the address (if present).
    # But to be more sure to have answere it would be great to manage async calls
    # to nominatim in such a queue in order to respect the time laps limit between calls.
    if not lon_lat is None:
        lon, lat = lon_lat
        point = Point((lon, lat))
        return Feature(
            id = row['sid'],
            geometry = point,
            properties = dict(row.properties, **updates)
        )

def champ(n=100):
    # WARNING: Do not run this version in parallel tasks.
    pages_ = db(db.page.id>0)._select(db.page.amenity_id)
    res = db(~db.amenity.id.belongs(pages_)).select(
        orderby = db.amenity.id,
        limitby = (0, n,) if not n is None else None,
        cacheable = True
    )
    return res.group_by_value(db.amenity.amenity)

def fetch(n=500, commit=False):
    """ Fetches amenities pages, caches html in local db and yields the geojson
    feature representing the amenity.
    """
    for amenity, res in champ(n).items():
        if amenity=='restaurant':
            picker = ResPicker()
        elif amenity=='hotel':
            picker = HotPicker()
        else:
            raise NotImplementedError

        for row,updates_ in tqdm(zip(
            res,
            picker(map(lambda r: r.url, res))
        ), total=len(res), desc='Fetching details'):
            lon_lat, updates, body = updates_
            feat = get_feature_(row, updates, lon_lat)

            db.page.insert(
                amenities_id = row.id,
                page = body
            )

            if not feat is None:
                yield feat
    if commit:
        db.commit()

async def fetchall_(res):
    """ Fetches amenities pages, caches html in local db and yields the geojson
    feature representing the amenity.
    """

    promeses_ = []
    for row in res:
        if  (row.source_name == settings.tripadvisor):
            if (row.amenity==RESTAURANT):
                browser = Restaurant(row.url)
            elif (row.amenity==HOTEL):
                browser = Hotel(row.url)
            elif (row.amenity==TOURISM):
                browser = Tourism(row.url)
            else:
                raise NotImplementedError
        elif (row.source_name == settings.immobiliareit):
            if (row.amenity==FORSALE):
                browser = ForSaleProp(row.url)
            else:
                raise NotImplementedError
        else:
            raise NotImplementedError
        promeses_.append(browser)

    # semaphoro = asyncio.Semaphore(10)
    # async with semaphoro:
    await asyncio.gather(*map(lambda p: p(), promeses_))

    return promeses_

def fetchall(champ=500, commit=False):

    pages_ = db(db.page.id>0)._select(db.page.amenity_id)
    baseset = db(
        (db.amenity.id > 0)
        # ~db.amenity.id.belongs(pages_) # & \
        # (db.amenity.source_name==settings.immobiliareit)
    )
    noa = baseset.count()

    if champ is None:
        champ = noa
    pbar = tqdm(total=noa, desc='Looping on total pages', nrows=2)
    for start in range(0, (noa//champ+1)*champ, champ):

        res = baseset.select(
            # WARNING: Sorting order here is important for later grouping!
            orderby = (db.amenity.source_name, db.amenity.id,),
            limitby = (start, start+champ-1,)
        )
        with Loop() as loop:
            all_updates = loop.run_until_complete(fetchall_(res))

        for upd,amenity in tqdm(zip(all_updates, res), desc='Looping on a chunk of features', total=len(res)):

            amenity.update_record(status_code = upd.status)

            if upd.status<400:

                page = db.page(amenity_id=amenity.id)
                if page is None:
                    page_id = db.page.insert(
                        amenity_id = amenity.id,
                        page = upd._body
                    )
                else:
                    page_id = page.id
                    checksum = db.page.checksum.compute(dict(page=upd._body))
                    if checksum!=page.checksum:
                        page.update_record(page = upd._body)

                for tb in upd.warnings:
                    db.log.insert(page_id=page_id, message=tb)
                # import pdb;pdb.set_trace();
                if not None in [upd.sid, upd.lon_lat]:

                    assert upd.details['sid'] == amenity['sid'], f"{amenity.sid} != {upd.details['sid']}"

                    lon, lat = upd.lon_lat
                    point = Point((lon, lat))
                    yield Feature(
                        id = amenity['sid'],
                        geometry = point,
                        properties = dict(amenity.properties, **upd.details),
                        source = amenity.source_name
                    )

            pbar.update(1)

        if commit:
            db.commit()

# def extract(n=None):
#     """ DEPRECATED """
#     res = db(db.page.amenities_id==db.amenity.id).select(
#         db.page.page.with_alias('page'),
#         db.amenity.amenity,
#         db.amenity.url.with_alias('url'),
#         # orderby = db.page.id,
#         limitby = (0, n,) if not n is None else None,
#         cacheable = True
#     )
#     for amenity, res in res.group_by_value(db.amenity.amenity).items():
#         if amenity=='restaurant':
#             details = res_details
#         elif amenity=='hotel':
#             details = hot_details
#         else:
#             raise NotImplementedError
#
#         for row in res:
#             updates = details(parser(row.page), row.url)
#             yield updates

def extract2():
    res = db(
        (db.amenity.status_code<400) & \
        (db.page.amenity_id==db.amenity.id)
    ).select(
        db.page.page.with_alias('page'),
        db.amenity.amenity.with_alias('amenity'),
        db.amenity.url.with_alias('url'),
        db.amenity.source_name.with_alias('source_name')
        # orderby = db.page.id,
        # limitby = (0, n,) if not n is None else None,
        # cacheable = True
    )

    for row in tqdm(res):

        if  (row.source_name == settings.tripadvisor):
            if (row.amenity==RESTAURANT):
                details = res_details
            elif (row.amenity==HOTEL):
                details = hot_details
            else:
                raise NotImplementedError
        elif (row.source_name == settings.immobiliareit):
            if (row.amenity==FORSALE):
                details = sal_details
            else:
                raise NotImplementedError
        else:
            raise NotImplementedError

        updates = details(parser(row.page), row.url)
        yield updates, row.source_name,


if __name__ == '__main__':
    populate(commit=True)
