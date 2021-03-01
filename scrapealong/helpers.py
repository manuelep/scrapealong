# -*- coding: utf-8 -*-

import asyncio
from diskcache import Cache
from functools import reduce
from urllib.parse import urljoin

import json
import numbers, datetime, types
from enum import Enum
from decimal import Decimal
import itertools
import nest_asyncio
nest_asyncio.apply()

class Accumulator(dict):
    """docstring for Info."""

    def __setitem__(self, key, value):
        if not key in self:
            self.__setattr__(key, itertools.count(start=1))
            dict.__setitem__(self, key, value)
        else:
            counter = next(getattr(self, key))
            dict.__setitem__(self, f"{key}:{counter}", value)

def objectify(obj):
    """ Courtesy of: https://github.com/web2py/py4web/blob/master/py4web/core.py#L222
    converts the obj(ect) into a json serializable object"""
    if isinstance(obj, numbers.Integral):
        return int(obj)
    elif isinstance(obj, (numbers.Rational, numbers.Real, Decimal,)):
        return float(obj)
    elif isinstance(obj, (datetime.date, datetime.datetime, datetime.time)):
        return obj.isoformat()
    elif isinstance(obj, str):
        return obj
    elif hasattr(obj, "__iter__") or isinstance(obj, types.GeneratorType):
        return list(obj)
    elif hasattr(obj, "xml"):
        return obj.xml()
    elif isinstance(
        obj, Enum
    ):  # Enum class handled specially to address self reference in __dict__
        return dict(name=obj.name, value=obj.value, __class__=obj.__class__.__name__)
    elif hasattr(obj, "__dict__") and hasattr(obj, "__class__"):
        d = dict(obj.__dict__)
        d["__class__"] = obj.__class__.__name__
        return d
    return str(obj)

def dumps(obj, sort_keys=True, indent=2):
    """ Courtesy of: https://github.com/web2py/py4web/blob/master/py4web/core.py#L247 """
    return json.dumps(obj, default=objectify, sort_keys=sort_keys, indent=indent)

CACHE_PATH = '/tmp/'

async def get_or_call(key, func, expire=60):
    with Cache(CACHE_PATH, disk_pickle_protocol=3) as cache:
        loop = asyncio.get_event_loop()
        try:
            result = await loop.run_in_executor(None, cache.get, key)
        except ValueError:
            result = None
        if result is None:
            val = await func()
            await loop.run_in_executor(None, cache.set, key, val, expire)
            result = await loop.run_in_executor(None, cache.get, key)
        return result

class Loop(object):
    """docstring for Loop."""

    def __init__(self):
        super(Loop, self).__init__()
        current_loop = asyncio.get_event_loop()
        if current_loop.is_closed():
            self.loop = asyncio.new_event_loop()
        else:
            self.loop = current_loop

    def __enter__(self):
        """ """
        return self.loop

    def __exit__(self, exc_type, exc_value, traceback):
        """ """
        # self.loop.close()

myurl = lambda *parts: reduce(lambda x, y: urljoin(x, y), parts)
