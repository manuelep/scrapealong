# -*- coding: utf-8 -*-

import os

# BASE_URL = 'https://www.tripadvisor.com'

PAGINATE = 30
PAGINATION_PREFIX = 'oa'

# db settings
LIB_FOLDER = os.path.dirname(__file__)
LIB_NAME = os.path.split(LIB_FOLDER)[-1]
# DB_FOLDER:    Sets the place where migration files will be created
#               and is the store location for SQLite databases
DB_FOLDER = "/tmp" # os.path.join(APP_FOLDER, "databases")
DB_URI = f"sqlite://{LIB_NAME}_temporary.db"
DB_POOL_SIZE = 1
DB_MIGRATE = True
DB_FAKE_MIGRATE = False

BASE_URLS_BY_SOURCE = {
    'tripadvisor': 'https://www.tripadvisor.com'
}

QUEUE_LENGTH = 10

TRIPADVISOR_HOTES_LOCATIONS = [
    # Examples
    # 'Hotels-g187849-Milan_Lombardy-Hotels.html',
]

TRIPADVISOR_RESTAURANTS_LOCATIONS = [
    # Examples
    # 'Restaurants-g187849-Milan_Lombardy.html',
]

# try import private settings
try:
    from .settings_private import *
except ModuleNotFoundError:
    pass
