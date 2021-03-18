# -*- coding: utf-8 -*-

import re
from tqdm import tqdm
from price_parser import Price
from decimal import Decimal
from ... helpers import Accumulator
from ..scrape import parse_script
import traceback
from ... common import logger

AMENITY = 'attraction'

def pagination(response):
    """ """
    pages = response.find('div', attrs={"data-automation": "AppPresentation_PaginationLinksList"}).findAll('a')
    return int(pages[-1].text)

def collection(response):
    """ """

    attractions_=response.find(
        "div",
        {"class":"_3W_31Rvp _1nUIPWja _3-Olh12m _2b3s5IMB"}
    ).findAll(
        "section",
        {"class":"_2TcutSHo _1QMAgDLV"}
    )

    infos = []
    for attraction in tqdm(attractions_, total=len(attractions_)):
        info = {'amenity': AMENITY}

        link_ = attraction.find("a",{"class":"fzO5lDuo _2hoC6Gk4 _11U11dRL _2fLMMA20"})
        if not link_ is None:
            info['url'] = link_['href']

        info['sid'] = next(filter(lambda ss: ss.startswith('d') and ss[1:].isdigit(), info['url'].split('-')))[1:]

        cost__ = attraction.find("div", {"class":"_392swiRT"}).find('div',{"class":"HLvj7Lh5 _1jvubpIi _3aNK9c7h"} )
        if not cost__ is None:
            cost_ = cost__.text
            price = Price.fromstring(cost_)
            info['price:{}'.format(price.currency)] = price.amount

        stars__ = attraction.find('div', {'class': '_2-JBovPw'})
        if not stars__ is None:
            stars_ = stars__.find('svg')

            stars, full_scale = sorted(re.findall(r'[\d]+[.,\d]+|[\d]*[.][\d]+|[\d]+', stars_.attrs['title']), key=float)
            starsn = Decimal(str(float(stars)/int(full_scale))).quantize(Decimal(str(1/int(full_scale))))
            info['stars:norm'] = starsn
            info['stars:raw'] = stars_.attrs['title']

            info['reviews'] = int(''.join(re.findall('[0-9]+', stars__.find('span').text)))

        name_ = attraction.find("div",{"class":"_1gpq3zsA _1zP41Z7X"})
        if not name_ is None:
            info['name'] = next(filter(lambda ss: ss.strip(), name_.findAll(text=True, recursive=False)))

        infos.append(info)

    return infos

def details(response):

    info = Accumulator()
    warnings = []

    sid_errors, sid_tbs = [], []

    try:
        scriptCode = response.find('script', text = re.compile("""typeahead.recentHistoryList"""), attrs = {"type":"text/javascript"})
        oo = parse_script(str(scriptCode), type='ATTRACTION')
        lat, lon = map(float, oo['coords'].split(','))
    except Exception as err:
        lon_lat, sid = None, None,
        warnings.append(traceback.format_exc())
        logger.warning(err)
    else:
        lon_lat = lon, lat,
        sid = str(oo['value'])
        info['sid'] = sid

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

    try:
        detail_type=response.find("a",{"class":"_1cn4vjE4"}).text
    except Exception as err:
        warnings.append(traceback.format_exc())
        logger.warning(err)
    else:
        info['detail:type'] = detail_type

    try:
        rank=response.find("div",{"class":"eQSJNhO6"}).text
        rank=re.search(r'[^a-zA-Z]*', rank)[0].strip()
        rank=re.sub(r'[^0-9]', '', rank)
    except Exception as err:
        warnings.append(traceback.format_exc())
        logger.warning(err)
    else:
        info['rank']=rank

    return sid, lon_lat, info, warnings,
