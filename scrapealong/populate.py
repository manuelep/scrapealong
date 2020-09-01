# -*- coding: utf-8 -*-

from .models import db
from .tripadvisor.fetchall import fetchall_
from .tripadvisor.settings import SOURCE_NAME as tripadvisor
from contextlib import contextmanager

from .tripadvisor.restaurants.single import Picker as ResPicker
from .tripadvisor.hotels.single import Picker as HotPicker

from geojson import Feature, Point
from tqdm import tqdm

def loopOdata(escape=None):
    for amenity in fetchall_():
        if escape is None or not amenity['sid'] in escape:
            if db.amenities(sid=amenity['sid']) is None:
                yield amenity

def populate(escape=None, commit=False):
    for amenity in loopOdata(escape=escape):
        db.amenities.insert(
            source_name = tripadvisor,
            properties = amenity
        )
    if commit:
        db.commit()

@contextmanager
def champ(n=100):
    # WARNING: Do not run this version in parallel tasks.
    try:
        res = db(db.amenities.id>0).select(
            orderby = db.amenities.id,
            limitby = (0, n,),
            cacheable = True
        )
        yield res.group_by_value(db.amenities.amenity)
    finally:
        db(db.amenities.id.belongs(map(lambda row: row.id, res))).delete()
        db.commit()

def get_feature_(row, updates_):
    lon_lat, updates = updates_

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

def extract(n=500):
    """ """
    with champ(n) as grouped:
        for amenity, res in grouped.items():
            if amenity=='restaurant':
                picker = ResPicker()
            elif amenity=='hotel':
                picker = HotPicker()
            else:
                raise NotImplementedError

            for row,updates_ in tqdm(zip(
                res,
                picker(map(lambda r: r.url, res))
            ), total=len(res)):
                feat = get_feature_(row, updates_)
                if not feat is None:
                    yield feat

if __name__ == '__main__':
    populate()
    db.commit()
