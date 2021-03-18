# -*- coding: utf-8 -*-

from json import loads
import re

def pagination(pages):
    """ """
    offset_=[int(x['data-offset'].strip()) for x in pages if int(x['data-offset'].strip())!=0]
    # pages_links=[x['href'] for x in pages]
    if offset_:
        total_offset=offset_[-1]/offset_[0]
        return total_offset
    else:
        return None

def parse_script(body, sid=None, **kwargs):
    res = re.search(r"taStore.store\('typeahead.recentHistoryList',(.*?)\)", body).group(1).strip()
    ss = loads(res)
    if sid is None:
        ll = list(filter(lambda dd: ('coords' in dd) and all([dd[k]==v for k,v in kwargs.items()]), ss))
        if len(ll)>1:
            import pdb; pdb.set_trace()
        return ll[0]
    else:
        return next(filter(lambda dd: str(dd['value'])==sid, ss))
