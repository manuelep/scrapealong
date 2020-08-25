# -*- coding: utf-8 -*-

from .models import db
from .tripadvisor.fetchall import fetchall_

def populate(escape=None):
    for amenity in fetchall_():
        if escape is None or not amenity['sid'] in escape:
            db.amenities.insert(properties=amenity)

if __name__ == '__main__':
    populate()
    db.commit()
