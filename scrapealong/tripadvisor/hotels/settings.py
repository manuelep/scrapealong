# -*- coding: utf-8 -*-

from ...settings import *

from ..settings import *

TRACKED_LOCATIONS = TRIPADVISOR_HOTES_LOCATIONS

"""HOTEL SCRAPE CONFIG"""

#COLLECTION (LIST PAGE CONSISTING OF 30 OR SO HOTELS)
HOTEL_MAIN_BLOCK="ui_column is-8 main_col allowEllipsis"
HOTEL_SID="data-locationid"
HOTEL_PRICE="price-wrap"
HOTEL_PRICE_PROVIDER=r'provider '
HOTEL_STARS=r'ui_bubble_rating bubble_'
HOTEL_REVIEWS="review_count"
HOTEL_NAME_LINK="property_title prominent"

#MAIN HOTEL DETAILS PAGE






"""RESTAURANT SCRAPE CONFIG """

"""TOURISM SCRAPE CONFIG """

# # try import private settings
# try:
#     from .settings_private import *
# except:
#     pass
