# -*- coding: utf-8 -*-

from ...settings import *

TRACKED_LOCATIONS = [
    # Examples
    # 'Restaurants-g187849-Milan_Lombardy.html',
]

# try import private settings
try:
    from .settings_private import *
except:
    pass
