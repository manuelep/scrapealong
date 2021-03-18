# -*- coding: utf-8 -*-

import re
from tqdm import tqdm
from price_parser import Price
from decimal import Decimal
import traceback
from ... helpers import Accumulator
from ..scrape import pagination as pagination_
from ... common import logger
from ..scrape import parse_script

PRICE_FULL_SCALE = 4
AMENITY = 'restaurant'

def pagination(response):
    """ """
    pages=pages=response.findAll("a",{"class":"pageNum taLnk"})
    return pagination_(pages)

def collection(response):
    """ """
    restaurants = response.findAll("div", {"class":"_1llCuDZj"})

    infos = []
    for restaurant in tqdm(restaurants,total=len(restaurants)):

        info = {'amenity': AMENITY}

        info['url'] = restaurant.find("a",{"class":"_15_ydu6b"})['href']
        info['sid'] = re.search('-d[0-9]+-', info['url']).group()[2:-1]

        reviews_ = restaurant.find("span",{"class":"w726Ki5B"})
        if not reviews_ is None:
            info['reviews'] = int(re.search('[0-9]+', reviews_.text).group())

        name_ = restaurant.find("a",{"class":"_15_ydu6b"})
        if not name_ is None:
            info['name'] = re.sub("(^\d. )","", name_.text)

        type_cost_ = restaurant.find("div",{"class":"MIajtJFg _1cBs8huC _3d9EnJpt"})
        if not type_cost_ is None:
            type_cost = type_cost_.findAll("span",{"class":"EHA742uW"})
            if type_cost:
                info['type'] = type_cost[0].text
                if len(type_cost)>1:
                    info['price:raw'] = type_cost[1].text
                    info['price:range:norm'] = list(map(
                        lambda seq: Decimal(
                            str(len(re.findall("\$", seq))/PRICE_FULL_SCALE)
                        ).quantize(Decimal(str(1/PRICE_FULL_SCALE))),
                        info['price:raw'].split('-')
                    ))

        # TODO: Implement here the calculation of other parameters useful for rating

        infos.append(info)

    return infos

def details(response):

    info = Accumulator()
    warnings = []
    sid_errors, sid_tbs = [], []

    try:
        sid = response.find("div", {"data-location-id": True})["data-location-id"]
    except Exception as err:
        sid_errors.append(err)
        sid_tbs.append(traceback.format_exc())
    else:
        info['sid'] = sid

    try:
        scriptCode = response.find('script', text = re.compile("""typeahead.recentHistoryList"""), attrs = {"type":"text/javascript"})
        oo = parse_script(scriptCode)
        lat, lon = map(float, ['coords'].split(','))
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

        try:
            name = response.find("h1", {"data-test-target": "top-info-header"}).text
        except Exception as err:
            sid_errors.append(err)
            sid_tbs.append(traceback.format_exc())
        else:
            info['name'] = name

        for err in sid_errors:
            logger.error(err)

        for tb in sid_tbs:
            warnings.append(tb)

    # TODO: Implement here the calculation of other parameters useful for rating

    try:
        price=None
        cuisines=None
        meals=None
        special_diets=None

        details=response.find("div",attrs={"class":"_3UjHBXYa"})
        s=details.findAll("div")
        s=[x for x in s if len(x.findAll("div"))>1]

        for x in s:
            if x.div.text.lower().startswith("price"):
                price=x.findAll("div")[-1].text
                price=re.sub('[^0-9-]+', '', price)
            elif x.div.text.lower().startswith("cuisines"):
                cuisines=x.findAll("div")[-1].text
            elif x.div.text.lower().startswith("meals"):
                meals=x.findAll("div")[-1].text
            elif x.div.text.lower().startswith("special"):
                special_diets=x.findAll("div")[-1].text
    except Exception as err:
        sid_errors.append(err)
        sid_tbs.append(traceback.format_exc())
    else:
        info['price'] = price
        info['cuisines'] = cuisines
        info['meals'] = meals
        info['special_diets'] = special_diets

    stars_ = response.find("span",{"class":"r2Cf69qf"})
    if not stars_ is None:
        info['stars:raw'] = float(re.search('[0-9/.]+', stars_.text).group())
        info['stars:norm'] = float(re.search('[0-9/.]+', stars_.text).group())/5.0
    else:
        info['stars:raw'] = 0.0
        info['stars:norm'] = 0.0

    return sid, lon_lat, info, warnings,
