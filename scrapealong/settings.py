# -*- coding: utf-8 -*-

BASE_URL = 'https://www.tripadvisor.com'

QUEUE_LENGTH = 10

PAGINATE = 30
PAGINATION_PREFIX = 'oa'

# db settings
# APP_FOLDER = os.path.dirname(__file__)
# APP_NAME = os.path.split(APP_FOLDER)[-1]
# DB_FOLDER:    Sets the place where migration files will be created
#               and is the store location for SQLite databases
DB_FOLDER = "/tmp" # os.path.join(APP_FOLDER, "databases")
DB_URI = "sqlite://tripadvisor_temporary.db"
DB_POOL_SIZE = 1
DB_MIGRATE = True
DB_FAKE_MIGRATE = False  # maybe?

# try import private settings
try:
    from .settings_private import *
except:
    pass
