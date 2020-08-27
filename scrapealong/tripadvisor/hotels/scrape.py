# -*- coding: utf-8 -*-

import re
from tqdm import tqdm
from price_parser import Price
from decimal import Decimal

AMENITY = 'hotel'

def pagination_(pages):
    """ """
    offset_=[int(x['data-offset'].strip()) for x in pages if int(x['data-offset'].strip())!=0]
    # pages_links=[x['href'] for x in pages]
    total_offset=offset_[-1]/offset_[0]
    return total_offset

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

import json

def details(response):

    info = {'amenity': AMENITY}

    rank_ = response.find("div",{"class":"_1vpp5J_x"})
    if not rank_ is None:
        info['rank:raw'] = response.find("div",{"class":"_1vpp5J_x"}).text
    #
    address_ = response.find("span",{"class":"_3ErVArsu jke2_wbp"})
    if not address_ is None:
        info['address'] = address_.text
    #
    # info['phone'] = response.find("a",{"class":"_1748LPGe"}).text
    #
    try:
        info['sid'] = response.find("div", {"data-locationid": True})["data-locationid"]
    except:
        info['sid'] = str(json.loads(response.find("div", {"data-ssrev-handlers": True})["data-ssrev-handlers"])['load'][3]['locationId'])

    #
    info['name'] = response.find("h1", {"id": "HEADING"}).text

    # TODO: Implement here the calculation of other parameters useful for rating

    return info
