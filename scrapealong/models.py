# -*- coding: utf-8 -*-

from .common import db
from . import settings

from urllib.parse import urljoin
from hashlib import blake2s
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

db.define_table("pages",
    Field("amenities_id", "reference amenities", required=True, notnull=True,
        # WARNING: Actually it's a one to one relationship
        unique = True
    ),
    # NOTE: Eventually we can think to store a compressed version
    Field("page", "text", required=True, notnull=True),
    Field("checksum", notnull=True, unique=True,
        compute = lambda row: blake2s(row['page'].encode('utf-8')).hexdigest()
    )
    # Field("info", "json")
)
