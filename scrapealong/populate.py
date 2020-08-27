# -*- coding: utf-8 -*-

from .models import db
from .tripadvisor.fetchall import fetchall_
from contextlib import contextmanager

def populate(escape=None, commit=False):
    for amenity in fetchall_():
        if escape is None or not amenity['sid'] in escape:
            if db.amenities(sid=amenity['sid']) is None:
                db.amenities.insert(properties=amenity)
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

if __name__ == '__main__':
    populate()
    db.commit()
