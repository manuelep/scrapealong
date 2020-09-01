# -*- coding: utf-8 -*-

from .common import db
from . import settings

from urllib.parse import urljoin
from pydal import Field

db.define_table("amenities",
    Field("sid", label="source id", unique=True, notnull=True,
        compute = lambda row: row['properties']['sid']
    ),
    Field("amenity", label="hotel, restaurant, etc.", notnull=True,
        compute = lambda row: row['properties']['amenity']
    ),
    Field("source_name", default="tripadvisor", required=True, notnull=True),
    Field("url", notnull=True, unique=True,
        compute = lambda row: urljoin(
            settings.BASE_URLS_BY_SOURCE[row['source_name']], row['properties']['url']
        )
    ),
    Field("properties", "json", required=True, notnull=True)
)
