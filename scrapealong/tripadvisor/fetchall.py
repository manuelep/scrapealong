# -*- coding: utf-8 -*-

from .hotels.fetchall import fetchall_ as fetchallhtl_
from .restaurants.fetchall import fetchall_ as fetchallrst_
from .turism.fetchall import fetchall_ as fetchalltur_

from itertools import chain

def fetchall_():
    for amenity in chain(fetchallhtl_(), fetchallrst_(), fetchalltur_()):
        yield amenity
