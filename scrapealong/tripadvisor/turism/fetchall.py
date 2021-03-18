# -*- coding: utf-8 -*-

from . import settings
from .multiple import Picker

def fetchall_():

    for location in settings.TRACKED_LOCATIONS:
        picker = Picker(location)
        for amenity in picker():
            yield amenity
