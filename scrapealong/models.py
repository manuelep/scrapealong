# -*- coding: utf-8 -*-

from .common import db

from pydal import Field

db.define_table("amenities",
    Field("sid", label="source id", unique=True, notnull=True,
        compute = lambda row: row['properties']['sid']
    ),
    Field("amenity", label="hotel, restaurant, etc.", notnull=True,
        compute = lambda row: row['properties']['amenity']
    ),
    Field("url", notnull=True, unique=True,
        compute = lambda row: row['properties']['url']
    ),
    Field("properties", "json", required=True, notnull=True)
)