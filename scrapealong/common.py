# -*- coding: utf-8 -*-

from . import settings

from pydal import DAL

# connect to db
db = DAL(
    settings.DB_URI,
    folder = settings.DB_FOLDER,
    pool_size = settings.DB_POOL_SIZE,
    migrate = settings.DB_MIGRATE,
    fake_migrate = settings.DB_FAKE_MIGRATE,
)
