# -*- coding: utf-8 -*-

from .common import db
from . import settings

from urllib.parse import urljoin
from hashlib import blake2s
from pydal import Field
import datetime

now = lambda : datetime.datetime.utcnow()

db.define_table("amenity",
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
    Field("properties", "json", required=True, notnull=True),
    Field("status_code", "integer", length=3, label="Response status code"),
    Field('created_on', 'datetime',
        default = now,
        writable=False, readable=False,
        # label = T('Created On')
    ),
    Field('modified_on', 'datetime',
        update=now, default=now,
        writable=False, readable=False,
        # label=T('Modified On')
    )
)

db.define_table("page",
    Field("amenity_id", "reference amenity", required=True, notnull=True,
        # WARNING: Actually it's a one to one relationship
        unique = True
    ),
    # NOTE: Eventually we can think to store a compressed version
    Field("page", "text", required=True, notnull=True),
    Field("checksum", notnull=True, unique=True,
        compute = lambda row: blake2s(row['page'].encode('utf-8')).hexdigest()
    ),
    Field('created_on', 'datetime',
        default = now,
        writable=False, readable=False,
        # label = T('Created On')
    ),
    Field('modified_on', 'datetime',
        update=now, default=now,
        writable=False, readable=False,
        # label=T('Modified On')
    )
)

db.define_table("log",
    Field("page_id", "reference page", required=True, notnull=True),
    Field("message", "text", required=True, notnull=True),
    Field('created_on', 'datetime',
        default = now,
        writable=False, readable=False,
        # label = T('Created On')
    )
)
