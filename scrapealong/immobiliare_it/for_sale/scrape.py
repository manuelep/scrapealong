# -*- coding: utf-8 -*-

from .. import settings
from ... common import logger
from ... helpers import Accumulator
import urllib
from price_parser import Price
import re, itertools
import traceback
from json import loads

AMENITY = "FOR SALE"

def get_price(txt):
    return float(re.findall(r'\d+', txt)[0])

get_surface = get_price

def provincie(resp):
    return list(map(
        lambda x: {'url': x.a['href'], 'state': x.a.text.strip()},
        resp.find(
            "div", {"class": "nd-searchesList__panel is-active"}
        ).findAll(
            "li", {"class": "nd-listMeta__item nd-listMeta__item--meta"}
        )
    ))

def comuni(resp, state):
    def main():
        res1 = resp.findAll("div", {"class": "nd-searchesList__block"})
        assert res1
        for comuni in res1:
            res2 = comuni.findAll("li", {"class": "nd-listMeta__item nd-listMeta__item--meta"})
            assert res2
            for comune in res2:
                yield ((state, comune.a.text.strip(),), comune.a['href'])

    return list(main())

def prop_pages(resp):
    nn_ = resp.find("ul",{"class":"pagination pagination__number"})
    if not nn_ is None:

        nn = nn_.findAll('li')[-1].text.strip()
        if nn.isnumeric():
            return int(nn)

    return 5

def properties_pages(resp):
    try:
        total_pages_=resp.find("a",{"class":"disabled","role":"button",
                                    "onclick":"return false"}).text.strip()
        total_pages_=''.join(e for e in total_pages_ if e.isnumeric())
        total_pages_=int(total_pages_)
    except:
        print(traceback.format_exc())
        try:
            total_page=resp.find("ul",{"class":"pagination pagination__number"})
            total_page=total_page.findAll("li")
            total_pages_=total_page[-1].text.strip()
            total_pages_=''.join(e for e in total_pages_ if e.isnumeric())
            total_pages_=int(total_pages_)
        except Exception as err2:
            print(err2)
            total_pages_=5
    return total_pages_

def properties(resp):
    for prop in resp.findAll("div", {"class": "listing-item_body--content"}):
        try:
            title_=prop.find("p",{"class":"titolo text-primary"})
        except:
            continue
        else:
            title_name=title_.a['title']
            title_link=title_.a['href']
            sid = re.search(r'/(\d+)/', title_link).group(1)
            property = title_name.split()[0]

            # try:
            #     title_=prop.find("p",{"class":"titolo text-primary"})
            # except:
            #     title_name="NO TITLE"
            #     title_link="NO TITLE LINK"
            # try:
            #     title_name=title_.a['title']
            # except:
            #     title_name="NO TITLE"
            # try:
            #     title_link=title_.a['href']
            # except:
            #     title_link="NO TITLE LINK"

            try:
                price_=prop.find("li",{"class":re.compile(r'lif__item lif__pricing')}).text.strip().replace('.', '')
                # price_ = int(re.findall(r'\d+', price_)[0])
            except:
                price_="NO PRICE"

            try:
                all_items=prop.findAll("li",{"class":re.compile(r'lif__item|lif__item hidden-xs')})
                room_='NO ROOMS'
                bathrooms_='NO BATHROOMS'
                floor_='NO FLOOR'
                surface_='NO SURFACE AREA'
                for item in all_items:
                    item_=item.text.strip()
                    try:
                        if "bathroom" in item_:
                            bathrooms_=" ".join(item_.split())
                        elif "room" in item_:#item.find("div",{"class":"lif__text lif--muted"}).text.strip()=='rooms':
                            room_=" ".join(item_.split())
                        elif "floor" in item_:
                            floor_=" ".join(item_.split())
                        elif "surface" in item_:
                            surface_=" ".join(item_.split()).replace('surface', '').strip().replace('.', '')
                    except:
                        continue

            except:
                room_='NO ROOMS'
                bathrooms_='NO BATHROOMS'
                floor_='NO FLOOR'
                surface_='NO SURFACE AREA'
            yield {
                # 'link':link_,
                'amenity': AMENITY,
                'contract': 'FOR SALE',
                'property': property,
                'title':title_name,
                'url':title_link,
                'price':price_,
                'bathrooms':bathrooms_,
                'surface':surface_,
                'floor':floor_,
                'rooms':room_,
                'sid': sid
            }

def clean(string):
        try:
            string=str(string)
            string=re.sub(' +', ' ', string)
            string=string.replace("\n","")
            string=string.strip()
            return string
        except:
            return string.strip()

def _loopOdefinitions(section):
    """ """
    return itertools.zip_longest(
        section.findAll("dt",{"class":re.compile(r'col-xs-12')}),
        section.findAll("dd",{"class":re.compile(r'col-xs-12')})
    )

def priceformat(cost):
    price = Price.fromstring(cost)
    return 'price:{}'.format(price.currency), price.amount

class Exceptions(object):
    """docstring for Exceptions."""

    def __init__(self):
        super(Exceptions, self).__init__()
        self.__errors = {}
        self.__tracebacks = {}

    def __setitem__(self, key, err):
        if key in self.__errors:
            self.__errors[key].append(err)
            self.__tracebacks[key].append(traceback.format_exc())
        else:
            self.__errors[key] = [err]
            self.__tracebacks[key] = [traceback.format_exc()]

    def __contains__(self, key):
        return (key in self.__errors)

    def clean(self, key):
        if key in self:
            del self.__errors[key]
            del self.__tracebacks[key]

    def __getitem__(self, key):
        return self.__errors[key]

    def loopOerrs(self, key):
        if key in self.__errors:
            for err in self.__errors[key]:
                yield err

    # def logit(self, key, method='warning'):
    #     if key in self.__errors:
    #         for err in self.__errors[key]:
    #             getattr(logger, method)(err)

    def as_list(self):
        return list(self.__tracebacks.values())


def details(response):
    """ property -> details """

    info = Accumulator()
    warnings = Exceptions()

    try:
        url = response.find('link', {'rel': 'canonical'})['href']
        sid = list(filter(
            None,
            url.split('/')
        ))[-1]
    except Exception as err:
        sid = None
        warnings['sid'] = err
    else:
        info['sid'] = sid

    # Extra lon-lat informations

    lon_lat = None

    try:
        bkg_img_url = response.find("div", {"data-background-image": re.compile("http")})["data-background-image"]
        center_ = re.search('center=(.*)&', bkg_img_url).group(0)
        lon_lat_ = urllib.parse.unquote(center_.split("&")[0][len('center='):]).split(',')[::-1]
        lon, lat = map(float, lon_lat_)
    except Exception as err:
        warnings['lon_lat'] = err
    else:
        lon_lat = [lon, lat]

    if 'lon_lat' in warnings:

        try:
            script_ = response.find("script", {"id": "js-hydration"}).contents[0]
            location_ = loads(script_)["listing"]["properties"][0]["location"]
        except Exception as err:
            warnings['lon_lat'] = err
        else:
            try:
                lon, lat = map(float, [location_['longitude'], location_['latitude']])
            except Exception as err:
                warnings['lon_lat'] = err
            else:
                lon_lat = [lon, lat]

            if location_.get('address'):
                info['address'] = location_['address']

            for nn in ['region', 'city', 'province', 'nation']:
                if location_.get(nn, {}).get('name'):
                    info[f'address:{nn}'] = location_[nn]['name']

    if lon_lat is None:
        for err in warnings.loopOerrs('lon_lat'):
            logger.error(err)
    else:
        warnings.clean('lon_lat')

    try:
        title = response.find('span', {'class': 'im-titleBlock__title'}).text.strip()
    except Exception as err:
        warnings['title'] = err
    else:
        info['title'] = title

    try:
        title = response.find('h1', {'class': 'raleway title-detail'}).text.strip()
    except Exception as err:
        warnings['title'] = err
    else:
        info['title'] = title

    if 'title' in info:
        warnings.clean('title')
    else:
        for err in warnings.loopOerrs('title'):
            logger.warning(err)
    try:
        address_ = response.find("span",{"class":re.compile(r"im-address__content js-map-address")})
        address_1 = re.sub(' +', ' ', address_.text.strip()).replace("\n","")
    except Exception as err:
        warnings['address'] = err
    else:
        info['address'] = address_1

    try:
        address_=response.find("span",{"class":re.compile(r"im-address__content js-map-address")})
        address_2 = address_.text.strip()
    except Exception as err:
        warnings['address'] = err
    else:
        info['address'] = address_2

    try:
        address_ = response.find("div",{"class": "im-map__description"})
        address_3 = address_.text.strip()
    except Exception as err:
        warnings['address'] = err
    else:
        info['address'] = address_3

    try:
        address_ = response.findAll("span", {"class": "im-location"})
        address_4 = ', '.join(map(lambda tag: tag.text.strip(), address_))
    except Exception as err:
        warnings['address'] = err
    else:
        info['address'] = address_4

    if "address" in info:
        warnings.clean('address')
    else:
        import pdb; pdb.set_trace()
        for err in warnings.loopOerrs("address"):
            logger.warning(err)

    mainFeatures_container = response.find('div', {'id': 'sticky-contact-bottom'})

    # surface, price = None, None

    if not mainFeatures_container is None:

        try:
            surface_container = mainFeatures_container.find('li', {'class': 'features__only-text'})
            info['surface'] = surface_container.text.strip() #.replace('.', '')
            surface = re.search("^[0-9]+", info['surface']).group(0)
        except Exception as err:
            warnings['surface'] = err
        else:
            if surface_:
                info['surface:m²'] = int(surface)

        try:
            price_container = mainFeatures_container.find('li', {'class': 'features__price'})
            cost_ = price_container.text
        except Exception as err:
            warnings['price'] = err
        else:
            pricekey, price = priceformat(cost_)
            info[pricekey] = price

    mainFeatures_container = response.find('div', {'class': 'im-mainFeatures'})

    if not mainFeatures_container is None:

        try:
            price_container = mainFeatures_container.find('li', {'class': 'im-mainFeatures__price'})
            cost_ = price_container.text.strip()
        except Exception as err:
            warnings['price'] = err
        else:
            pricekey, price = priceformat(cost_)
            info[pricekey] = price

        for item in mainFeatures_container.findAll('li'):
            title_ = item.find("span", {'class': 'im-mainFeatures__label'})
            if not title_ is None:
                value_ = item.find("span", {'class': 'im-mainFeatures__value'})
                if value_ is None:
                    import pdb; pdb.set_trace()
                symbol_ = value_.find("span", {'class': 'im-mainFeatures__symbol'})
                if not symbol_ is None:
                    symbol = symbol_.text or ''
                else:
                    symbol = ''

                key = f"{title_.text}"
                if symbol:
                    key += f":{symbol}"
                value = clean(value_.text.strip())
                if key.startswith("surface"):
                    value = int(re.search("^[0-9]+", value).group(0))

                info[key] = value

    if not 'price' in info:
        for err in warnings.loopOerrs("price"):
            logger.error(err)
    else:
        warnings.clean('price')

    if not 'surface:m²' in info:
        for err in warnings.loopOerrs('surface'):
            logger.error(err)
    else:
        warnings.clean('surface')

    try:
        for section in response.findAll("div",{"class":"row section-data"}):
            section_title = section.find("h3")
            if section_title is None:
                continue
            if any(map(
                lambda t: (t in section_title.text),
                ("Main", "Expenses", "Energy",)
            )):
                for kw in _loopOdefinitions(section):
                    try:
                        key, value = map(lambda kw_: str(kw_.text), kw)
                    except Exception as err:
                        warnings[key] = err
                    else:
                        if any(map(
                            lambda t: (t in key),
                            [
                                "Reference and ad Date", "Contract", "Type", "Surface",
                                "Rooms", "Floor", "Availability", "Property type",

                                "Price", "Condominium", "Cadastral information",

                                "Condition", "Heating", "Air", "Energy", "Global", "Year"
                            ]
                        )):
                            if "Price" in key:
                                pricekey, pricevalue = priceformat(clean(value))
                                info[pricekey] = pricevalue.strip()
                            else:
                                info[key.lower()] = clean(value)
    except Exception as err:
        warnings.append(traceback.format_exc())

    return sid, lon_lat, info, warnings.as_list()

def property(response):
    """ DEPRECATED """

    title_ = response.find('span', {'class': 'im-titleBlock__title'})
    title = title_ and title_.text.strip()

    # url_ = response.find('link', {'rel': 'canonical'})['href']

    bkg_img_url = response.find("div", {"data-background-image": re.compile("http")})["data-background-image"]
    lon_lat = urllib.parse.unquote(re.search('center=(.*)&', bkg_img_url).group(0).split("&")[0][len('center='):]).split(',')[::-1]

    sticky_contact_bottom = response.find('div', {'id': 'sticky-contact-bottom'})
    surface_container = sticky_contact_bottom and sticky_contact_bottom.find('li', {'class': 'features__only-text'})
    price_container = sticky_contact_bottom and sticky_contact_bottom.find('li', {'class': 'features__price'})

    reference_ad_date_=None
    contract_=None
    type_=None

    surface_ = surface_container and surface_container.text.strip().replace('.', '')
    rooms_=None
    floor_=None
    availability_=None
    property_type_=None
    price_= price_container and price_container.text.strip().replace('.', '')
    condominium_fees_=None
    condition_=None
    heating_=None
    air_conditioner_=None
    energy_class_=None
    global_energy_=None
    cadastrial_info_=None
    year_of_constraction_=None

    for resp in response.find("div",{"class":"row section-data"}):
        try:
            cur_resp=resp.text.strip().split()[0]
        except (AttributeError, IndexError):
            continue

        if "Main" in cur_resp:
            try:

                main_page_=all_pages.find("dl",{"class":"col-xs-12"})
                all_main_items_keys_=main_page_.findAll("dt",{"class":re.compile(r'col-xs-12')})
                all_main_items_values_=main_page_.findAll("dd",{"class":re.compile(r'col-xs-12')})

                for item in itertools.zip_longest(all_main_items_keys_,all_main_items_values_):
                    key_str=item[0].text
                    value_str=item[1].text
                    if "Reference and ad Date" in str(key_str):
                        reference_ad_date_=str(value_str)
                    elif "Contract" in str(key_str):
                        contract_=clean(str(value_str))
                    elif "Type" in str(key_str):
                        type_=clean(str(value_str))
                    elif "Surface" in str(key_str):
                        surface_=clean(str(value_str))
                    elif "Rooms" in str(key_str):
                        rooms_=clean(str(value_str))
                    elif "Floor" in str(key_str):
                        floor_=clean(str(value_str))
                    elif "Availability" in str(key_str):
                        availability_=clean(str(value_str))
                    elif "Property type" in str(key_str):
                        property_type_=clean(str(value_str))
            except:
                # raise
                kkk=0
        elif "Features" in cur_resp:
            try:
                features_all=resp.findAll("span")
                features_all=[x.text for x in features_all]
                features_all=",".join(x for x in features_all)
            except:
                kkk=0
        elif "Expenses" in cur_resp:
            try:
                all_expenses_items_keys_=resp.findAll("dt",{"class":re.compile(r'col-xs-12')})
                all_expenses_items_values_=resp.findAll("dd",{"class":re.compile(r'col-xs-12')})
                for item in itertools.zip_longest(all_expenses_items_keys_,all_expenses_items_values_):
                    key_str=item[0].text
                    value_str=item[1].text
                    # if "Price" in str(key_str):
                    #     price_=clean(str(value_str))
                    if "Condominium" in str(key_str):
                        condominium_fees_=clean(str(value_str))
                    elif "Cadastral information" in str(key_str):
                        cadastrial_info_ = clean(str(value_str))
            except:
                kkk=0
        elif "Energy" in cur_resp:
            try:
                all_energy_items_keys_=resp.findAll("dt",{"class":re.compile(r'col-xs-12')})
                all_energy_items_values_=resp.findAll("dd",{"class":re.compile(r'col-xs-12')})
                for item in itertools.zip_longest(all_energy_items_keys_,all_energy_items_values_):
                    key_str=item[0].text
                    value_str=item[1].text
                    if "Condition" in str(key_str):
                        condition_=clean(str(value_str))
                    elif "Heating" in str(key_str):
                        heating_=clean(str(value_str))
                    elif "Air" in str(key_str):
                        air_conditioner_=clean(str(value_str))
                    elif "Energy" in str(key_str):
                        energy_class_=clean(str(value_str))
                    elif "Global" in str(key_str):
                        global_energy_=clean(str(value_str))
                    elif "Year" in str(key_str):
                        year_of_constraction_=clean(str(value_str))
            except:
                kkk=0
    try:
        address_=response.find("span",{"class":re.compile(r"im-address__content js-map-address")}).text.strip()
        address_=re.sub(' +', ' ', address_)
        address_=address_.replace("\n","")
    except:
        try:
            address_=response.find("span",{"class":re.compile(r"im-address__content js-map-address")}).text.strip()
        except:
            address_=None

    return lon_lat, {
        # 'title_link':url,
        # 'url': url_,
        'reference and ad Date':reference_ad_date_,
        'contract':contract_,
        'type':type_,
        'surface':surface_,
        'rooms':rooms_,
        'floor':floor_,
        'availability':availability_,
        'property type':property_type_,
        'price':price_,
        'condominium fees':condominium_fees_,
        'condition':condition_,
        'heating':heating_,
        'air conditioner':air_conditioner_,
        'energy class':energy_class_,
        'address':address_,
        'year of contruction': year_of_constraction_
    }
