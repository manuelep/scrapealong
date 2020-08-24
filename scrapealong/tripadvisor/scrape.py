# -*- coding: utf-8 -*-

def pagination(pages):
    """ """
    offset_=[int(x['data-offset'].strip()) for x in pages if int(x['data-offset'].strip())!=0]
    # pages_links=[x['href'] for x in pages]
    total_offset=offset_[-1]/offset_[0]
    return total_offset
