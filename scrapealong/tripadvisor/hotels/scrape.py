# -*- coding: utf-8 -*-

import json
import re
from tqdm import tqdm
from price_parser import Price
from decimal import Decimal
import traceback
from ... common import logger
from ... helpers import Accumulator

from ..scrape import parse_script

from itertools import zip_longest
# from ..scrape_conf import *

from . import settings

AMENITY = 'hotel'

def pagination_(pages):
    """ """
    offset_=[int(x['data-offset'].strip()) for x in pages if int(x['data-offset'].strip())!=0]
    total_offset=offset_[-1]/offset_[0]
    return total_offset

def pagination(response):
    """ """
    pages=response.findAll("a",{"class":re.compile(r'pageNum')})
    return pagination_(pages)

def collection(response):
    """ """
    hotels_=response.findAll("div",{"class": settings.HOTEL_MAIN_BLOCK})

    infos = []
    for hotel in tqdm(hotels_,total=len(hotels_)):
        info = {'amenity': AMENITY}

        info['sid'] = hotel.find("div", {settings.HOTEL_SID: re.compile(".")})[settings.HOTEL_SID]

        cost__ = hotel.find("div",{"class": settings.HOTEL_PRICE})
        if not cost__ is None:
            cost_ = cost__.find("div",{"class":re.compile(r'price ')}).text
            price = Price.fromstring(cost_)
            info['price:{}'.format(price.currency)] = price.amount

        provider_ = hotel.find("div",{"class":re.compile(settings.HOTEL_PRICE_PROVIDER)})
        if not provider_ is None:
            info['provider'] = provider_.text

        stars__ = hotel.find("a",{"class":re.compile(settings.HOTEL_STARS)})
        if not stars__ is None:
            info['stars:raw'] = stars__['alt']
            stars_, full_scale = [x[0] for x in re.finditer('[\d]*[.][\d]+|[\d]+', stars__['alt'])]
            stars = Decimal(str(float(stars_)/int(full_scale))).quantize(Decimal(str(1/int(full_scale))))
            info['stars:norm'] = stars
        else:
            info['stars:raw'] = 0.0
            info['stars:norm'] = 0.0
        reviews_ = hotel.find("a",{"class": settings.HOTEL_REVIEWS})
        if not reviews_ is None:
            info['reviews'] = int(re.search('[0-9]+', reviews_.text).group())
            info['views'] = int(re.search('[0-9]+', reviews_.text).group()) * 4
        else:
            info['reviews']=0
            info['views'] = 0
        name_ = hotel.find("a",{"class": settings.HOTEL_NAME_LINK})
        if not name_ is None:
            info['name'] = name_.text.replace('"','')

        link_ = hotel.find("a",{"class": settings.HOTEL_NAME_LINK})
        if not link_ is None:
            info['url'] = link_['href']

        # TODO: Implement here the calculation of other parameters useful for rating

        infos.append(info)

    return infos


def details(response):

    info = Accumulator()
    warnings = []

    sid_errors, sid_tbs = [], []

    try:
        sid = response.find('input', {'name': 'locationId'})['value']
    except Exception as err:
        sid_errors.append(err)
        sid_tbs.append(traceback.format_exc())
    else:
        info['sid'] = sid

    if sid_errors:
        for foo in response.findAll("div", {"data-ssrev-handlers": True}):
            try:
                sid = str(json.loads(foo["data-ssrev-handlers"])['load'][3]['locationId'])
            except Exception as err:
                sid_errors.append(err)
                sid_tbs.append(traceback.format_exc())
                continue
            else:
                sid_errors, sid_tbs = [], []
                break

    if sid_errors:

        for script in response.find('body').findAll("script"):
            if re.search('locationId', str(script)):
                if re.search('locationId\"', str(script)):
                    sid = re.search('locationId\".*?,', str(script)).group()[len('locationId')+2:-1]
                    break

    try:
        info['sid'] = sid
    except NameError as err:
        sid = None
        sid_errors.append(err)
        sid_tbs.append(traceback.format_exc())
    else:
        sid_errors, sid_tbs = [], []

    for err in sid_errors:
        logger.error(err)

    for tb in sid_tbs:
        warnings.append(tb)

    try:
        scriptCode = response.find('script', text = re.compile("""typeahead.recentHistoryList"""), attrs = {"type":"text/javascript"})
        oo = parse_script(str(scriptCode), sid)
        lat, lon = map(float, oo['coords'].split(','))
    except Exception as err:
        lon_lat = None
        warnings.append(traceback.format_exc())
        logger.warning(err)
    else:
        lon_lat = lon, lat,

        try:
            info['url'] = oo['url']
        except Exception as err:
            warnings.append(traceback.format_exc())
            logger.warning(err)

        try:
            info['name'] = oo['details']['name']
        except Exception as err:
            warnings.append(traceback.format_exc())
            logger.warning(err)

    if not 'name' in info:
        name_ = response.find("h1", {"id": "HEADING"})
        try:
            name = name_.text.strip()
        except Exception as err:
            warnings.append(traceback.format_exc())
            logger.warning(err)
        else:
            info['name'] = name

    rank_ = response.find("div",{"class":"_1vpp5J_x"})
    try:
        rank_ = response.find("div",{"class":"_1vpp5J_x"}).text.strip()
        rank = ' '.join(filter(None, re.split(' |\n',rank_)))

    except Exception as err:
        warnings.append(traceback.format_exc())
        logger.warning(err)
    else:
        info['rank:raw'] = rank

    address_ = response.find("span",{"class":"_3ErVArsu jke2_wbp"})
    try:
        address = address_.text.strip()
    except Exception as err:
        warnings.append(traceback.format_exc())
        logger.warning(err)
    else:
        info['address'] = address

    try:
        phone = response.find("a",{"class":"_1748LPGe"}).text
    except Exception as err:
        warnings.append(traceback.format_exc())
        logger.warning(f"Phone number not found: {err}")
    else:
        info['phone'] = phone

    # TODO: Implement here the calculation of other parameters useful for rating

    property_amenities_name=[]
    property_amenities_cat=[]
    room_features_name=[]
    room_features_cat=[]
    room_types_name=[]
    room_types_cat=[]

    try:

        about_ = response.findAll("div", attrs={"class":"ui_columns _318JyS8B"})
        about = next(filter(lambda x:"Property amenities" in x.text,  about_))

        about_ui_ = about.findAll("div",{"class":"ui_column"})
        about_ui = next(filter(lambda x:"Property amenities" in x.text,  about_ui_))

        about_info = json.loads(about_ui.div["data-ssrev-handlers"])
        abouts = about_info['load'][3]['amenities']

        property_amenities = abouts['highlightedAmenities']['propertyAmenities']+abouts['nonHighlightedAmenities']['propertyAmenities']
        room_features = abouts['highlightedAmenities']['roomFeatures']+abouts['nonHighlightedAmenities']['roomFeatures']
        room_types = abouts['highlightedAmenities']['roomTypes']+abouts['nonHighlightedAmenities']['roomTypes']

        for x,y,z in zip_longest(property_amenities,room_features,room_types):

            if not x==None:
                property_amenities_name.append(x['amenityNameLocalized'])
                property_amenities_cat.append(x['amenityCategoryName'])
            if not y==None:
                room_features_name.append(y['amenityNameLocalized'])
                room_features_cat.append(y['amenityCategoryName'])
            if not z==None:
                room_types_name.append(z['amenityNameLocalized'])
                room_types_cat.append(z['amenityCategoryName'])

    except Exception as err:
        warnings.append(traceback.format_exc())
        logger.warning(err)
    else:
        info['property_amenities_name'] = property_amenities_name
        info['property_amenities_cat'] = property_amenities_cat
        info['room_features_name'] = room_features_name
        info['room_features_cat'] = room_features_cat
        info['room_types_name'] = room_types_name
        info['room_types_cat'] = room_types_cat

    return sid, lon_lat, info, warnings,
