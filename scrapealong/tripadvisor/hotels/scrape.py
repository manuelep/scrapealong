# -*- coding: utf-8 -*-

import json
import re
from tqdm import tqdm
from price_parser import Price
from decimal import Decimal
import traceback
from ... common import logger
from ... helpers import Accumulator
from ..scrape import pagination as pagination

AMENITY = 'hotel'

# def pagination_(pages):
#     """ """
#     offset_=[int(x['data-offset'].strip()) for x in pages if int(x['data-offset'].strip())!=0]
#
#     try:
#         total_offset=offset_[-1]/offset_[0]
#     except IndexError:
#         import pdb; pdb.set_trace()
#     return total_offset

def pagination(response):
    """ """
    pages=response.findAll("a",{"class":re.compile(r'pageNum')})
    return pagination_(pages)

def collection(response):
    """ """
    hotels_=response.findAll("div",{"class":"ui_column is-8 main_col allowEllipsis"})

    infos = []
    for hotel in tqdm(hotels_,total=len(hotels_)):
        info = {'amenity': AMENITY}

        info['sid'] = hotel.find("div", {"data-locationid": re.compile(".")})['data-locationid']

        cost__ = hotel.find("div",{"class":"price-wrap"})
        if not cost__ is None:
            cost_ = cost__.find("div",{"class":re.compile(r'price ')}).text
            price = Price.fromstring(cost_)
            info['price:{}'.format(price.currency)] = price.amount

        provider_ = hotel.find("div",{"class":re.compile(r'provider ')})
        if not provider_ is None:
            info['provider'] = provider_.text

        stars__ = hotel.find("a",{"class":re.compile(r'ui_bubble_rating bubble_')})
        if not stars__ is None:
            info['stars:raw'] = stars__['alt']
            stars_, full_scale = [x[0] for x in re.finditer('[\d]*[.][\d]+|[\d]+', stars__['alt'])]
            stars = Decimal(str(float(stars_)/int(full_scale))).quantize(Decimal(str(1/int(full_scale))))
            info['stars:norm'] = stars

        reviews_ = hotel.find("a",{"class":"review_count"})
        if not reviews_ is None:
            info['reviews'] = int(re.search('[0-9]+', reviews_.text).group())

        name_ = hotel.find("a",{"class":"property_title prominent"})
        if not name_ is None:
            info['name'] = name_.text.replace('"','')

        link_ = hotel.find("a",{"class":"property_title prominent"})
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
        logger.warning(err)
    else:
        info['phone'] = phone

    name_ = response.find("h1", {"id": "HEADING"})
    try:
        name = name_.text.strip()
    except Exception as err:
        warnings.append(traceback.format_exc())
        logger.warning(err)
    else:
        info['name'] = name

    # TODO: Implement here the calculation of other parameters useful for rating

    return sid, info, warnings
