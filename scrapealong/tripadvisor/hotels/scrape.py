# -*- coding: utf-8 -*-

import re
from tqdm import tqdm
from price_parser import Price
from decimal import Decimal
from ..scrape import pagination as pagination_

def pagination(response):
    """ """
    pages=response.findAll("a",{"class":re.compile(r'pageNum')})
    return pagination_(pages)

def collection(response):
    """ """
    hotels_=response.findAll("div",{"class":"ui_column is-8 main_col allowEllipsis"})

    infos = []
    for hotel in tqdm(hotels_,total=len(hotels_)):
        info = {'amenity': 'hotel'}

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

        infos.append(info)

    return infos
