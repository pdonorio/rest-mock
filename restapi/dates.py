# -*- coding: utf-8 -*-

# import time
# import datetime
import timestring
import dateutil.parser


def set_date_period(date, objdate, code='start'):
    du = dateutil.parser.parse(date[code])
    t = timestring.Date(du)
    objdate['years'][code] = t.year
    objdate['months'][code] = t.month
    objdate['days'][code] = t.day
    return objdate


def convert_to_ordered_string(date):
    """
    date = {
        'start': ... ,
        'end': ... ,
        'year': ... ,
    }
    """
    objdate = {
        'years': {'start': None, 'end': None},
        'months': {'start': None, 'end': None},
        'days': {'start': None, 'end': None}
    }

    if 'year' in date:
        # String representation
        tmp = str(date['year'])
        objdate['years']['start'] = tmp
        objdate['years']['end'] = tmp

    if 'start' in date:
        objdate = set_date_period(date, objdate, code='start')

    if 'end' in date:
        objdate = set_date_period(date, objdate, code='end')

    # build the date string to show inside the search like
    # 1622 / 03-04 / 11-19
    newyear = str(objdate['years']['start'])
    if objdate['years']['end'] != objdate['years']['start']:
        newyear += '-' + str(objdate['years']['end'])

    newmonth = ' '
    if objdate['months']['start'] is not None:
        newmonth += str(objdate['months']['start']).zfill(2)
    if objdate['months']['end'] is not None:
        if objdate['months']['end'] != objdate['months']['start']:
            if newmonth != '':
                newmonth += '-'
            newmonth += str(objdate['months']['end']).zfill(2)

    newday = ' '
    if objdate['days']['start'] is not None:
        newday += str(objdate['days']['start']).zfill(2)
    if objdate['days']['end'] is not None:
        if objdate['days']['end'] != objdate['days']['start']:
            if newday != '':
                newday += '-'
            newday += str(objdate['days']['end']).zfill(2)

    # final_date = newday + newmonth + newyear
    final_date = newyear + newmonth + newday

    return final_date
