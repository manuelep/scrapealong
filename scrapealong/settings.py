# -*- coding: utf-8 -*-

BASE_URL = 'https://www.tripadvisor.com'

QUEUE_LENGTH = 10

PAGINATE = 30
PAGINATION_PREFIX = 'oa'

# try import private settings
try:
    from .settings_private import *
except:
    pass
