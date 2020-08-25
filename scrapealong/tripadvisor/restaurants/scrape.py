# -*- coding: utf-8 -*-

import re
from tqdm import tqdm
from price_parser import Price
from decimal import Decimal
from ..scrape import pagination as pagination_

PRICE_FULL_SCALE = 4

def pagination(response):
    """ """
    pages=pages=response.findAll("a",{"class":"pageNum taLnk"})
    return pagination_(pages)

def collection(response):
    """ """
    restaurants = response.findAll("div", {"class":"_1llCuDZj"})

    infos = []
    for restaurant in tqdm(restaurants,total=len(restaurants)):

        info = {'amenity': 'restautant'}

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
                        lambda seq: Decimal(str(len(re.findall("\$", seq))/4)).quantize(Decimal(str(1/PRICE_FULL_SCALE))),
                        info['price:raw'].split('-')
                    ))

        infos.append(info)

    return infos
