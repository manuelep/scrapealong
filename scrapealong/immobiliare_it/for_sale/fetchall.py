# -*- coding: utf-8 -*-

from ... import settings
from .multiple import Picker

def fetchall():
    picker = Picker()
    for amenity in picker(*settings.IMMOBILIARE_LOCATIONS):
        yield amenity
