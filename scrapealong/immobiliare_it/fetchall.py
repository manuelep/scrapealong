# -*- coding: utf-8 -*-

from .for_sale.fetchall import fetchall as fetchallsal_

from itertools import chain

def fetchall_():
    for amenity in chain(fetchallsal_()):
        yield amenity
