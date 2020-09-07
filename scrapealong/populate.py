# -*- coding: utf-8 -*-

from .models import db
from .tripadvisor.fetchall import fetchall_
from .tripadvisor.settings import SOURCE_NAME as tripadvisor
from contextlib import contextmanager

from .tripadvisor.restaurants.single import Picker as ResPicker
from .tripadvisor.hotels.single import Picker as HotPicker

from .tripadvisor.restaurants.scrape import details as res_details
from .tripadvisor.hotels.scrape import details as hot_details

from .fetch import parser

from geojson import Feature, Point
from tqdm import tqdm

def loopOdata(escape=None):
    for amenity in fetchall_():
        if escape is None or not amenity['sid'] in escape:
            if db.amenities(sid=amenity['sid']) is None:
                yield amenity

def populate(escape=None, commit=False):
    """ Populates the local temporary database with raw informtions from summary
    pages.
    """
    for amenity in loopOdata(escape=escape):
        db.amenities.insert(
            source_name = tripadvisor,
            properties = amenity
        )
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
    pages_ = db(db.pages.id>0)._select(db.pages.amenities_id)
    res = db(~db.amenities.id.belongs(pages_)).select(
        orderby = db.amenities.id,
        limitby = (0, n,) if not n is None else None,
        cacheable = True
    )
    return res.group_by_value(db.amenities.amenity)

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

            db.pages.insert(
                amenities_id = row.id,
                page = body
            )

            if not feat is None:
                yield feat
    if commit:
        db.commit()

# def page2properties(updates):
#     lon, lat = lon_lat
#     point = Point((lon, lat))
#     return Feature(
#         id = updates['sid'],
#         geometry = point,
#         properties = dict(updates)
#     )

def extract(n=None):
    """ """
    res = db(db.pages.amenities_id==db.amenities.id).select(
        db.pages.page.with_alias('page'),
        db.amenities.amenity,
        db.amenities.url.with_alias('url'),
        # orderby = db.pages.id,
        limitby = (0, n,) if not n is None else None,
        cacheable = True
    )
    for amenity, res in res.group_by_value(db.amenities.amenity).items():
        if amenity=='restaurant':
            details = res_details
        elif amenity=='hotel':
            details = hot_details
        else:
            raise NotImplementedError

        for row in res:
            updates = details(parser(row.page), row.url)
            yield updates

def extract2():
    res = db(db.pages.amenities_id==db.amenities.id).select(
        db.pages.page.with_alias('page'),
        db.amenities.amenity.with_alias('amenity'),
        db.amenities.url.with_alias('url'),
        # orderby = db.pages.id,
        # limitby = (0, n,) if not n is None else None,
        # cacheable = True
    )

    for row in res:
        if row.amenity=='restaurant':
            details = res_details
        elif row.amenity=='hotel':
            details = hot_details
        else:
            raise NotImplementedError
        updates = details(parser(row.page), row.url)
        yield updates


if __name__ == '__main__':

    # import argparse
    #
    # parser = argparse.ArgumentParser(description='Populate the local temporary database')
    #
    # parser.add_argument('-c', '--champ', help='')
    #
    # args = parser.parse_args()


    populate()


    # feats = list(extract())

    # feats = list(fetch(None))
    # db.commit()
