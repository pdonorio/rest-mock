# -*- coding: utf-8 -*-

import re
import logging
import datetime
from beeprint import pp
from restapi.resources.services.rethink import RethinkConnection, RDBquery
from restapi.resources.services.uploader import ZoomEnabling
from restapi.resources.services.elastic import \
    BASE_SETTINGS, ES_SERVICE, \
    HTML_ANALYZER, EL_INDEX0, EL_INDEX1, EL_INDEX2, EL_INDEX3, \
    EL_TYPE1, EL_TYPE2

from elasticsearch import Elasticsearch
from restapi import get_logger
from restapi.dates import set_date_period
from restapi.commons.conversions import Utils

RDB_TABLE1 = "datavalues"
RDB_TABLE2 = "datadocs"
noimages = {}
toberemoved = [
    # 'd2d5fcb6-81cc-4654-9f65-a436f0780c67'  # prova
]

fields = [
    'extrait', 'source', 'fete',
    'transcription', 'traduction',
    'date', 'lieu', 'manuscrit',
    'temps', 'actions', 'apparato',
]

# INDEX 1 is NORMAL SEARCH FILTER

INDEX_BODY1 = {
    'settings': BASE_SETTINGS,
    'mappings': {
        EL_INDEX1: {
            '_all': {
                "analyzer": "nGram_analyzer",
                "search_analyzer": "whitespace_analyzer"
            },
            # index specifications
            'properties': {
                "extrait": {
                    "type": "string",
                    "index": "not_analyzed"
                },
                "page": {
                    "type": "string",
                    "index": "not_analyzed"
                },

                ####################
                "source": {
                    "type": "string",
                    "index": "not_analyzed"
                },
                "fete": {
                    "type": "string",
                    "index": "not_analyzed"
                },
                "date": {
                    "type": "string",
                    "index": "not_analyzed",
                    "include_in_all": False
                },
                "lieu": {
                    "type": "string",
                    "index": "not_analyzed",
                    "include_in_all": False
                },
                "manuscrit": {
                    "type": "string",
                    "index": "not_analyzed",
                    "include_in_all": False
                },
                "temps": {
                    "type": "string",
                    "index": "not_analyzed",
                    "include_in_all": False
                },
                "actions": {
                    "type": "string",
                    "index": "not_analyzed",
                    "include_in_all": False
                },
                "apparato": {
                    "type": "string",
                    "index": "not_analyzed",
                    "include_in_all": False
                },
                "gravure": {
                    "type": "boolean",
                    "index": "not_analyzed",
                    "include_in_all": False
                },
                "langue": {
                    "type": "string",
                    "index": "not_analyzed",
                    "include_in_all": False
                },

                ####################
                "start_date": {
                    "type": "date",
                    # "format": "yyyy-MM-dd"
                    "include_in_all": False
                },
                "end_date": {
                    "type": "date",
                    # "format": "yyyy-MM-dd"
                    "include_in_all": False
                },
                ####################

                # "sort_string": {
                #     "type": "string",
                #     "include_in_all": False
                # },
                "extrait_number": {
                    "type": "integer",
                    "include_in_all": False
                },
                "sort_number": {
                    "type": "integer",
                    "include_in_all": False
                },
                "transcription": {
                    "type": "string",
                    "analyzer": "nGram_analyzer",
                    "search_analyzer": "whitespace_analyzer"
                },
                "traduction": {
                    "type": "string",
                    "analyzer": "nGram_analyzer",
                    "search_analyzer": "whitespace_analyzer"
                },
                "thumbnail": {
                    "type": "string",
                    "index": "no",
                    "include_in_all": False
                },
            }
        }
    }
}

INDEX_BODY2 = {
    # INDEX 2 is SUGGESTIONs!!
    'settings': BASE_SETTINGS,
    'mappings': {
        EL_INDEX2: {
            'properties': {
                "suggest": {
                    "type": "string",
                    "analyzer": "nGram_analyzer"
                    # tokenizers?
                },
                "original": {
                    "type": "string",
                    "index": "not_analyzed"
                },
                "label": {
                    "type": "string",
                    "index": "not_analyzed"
                }
            }
        }
    }
}

SUGGEST = 'suggest'

logger = get_logger(__name__)
logger.setLevel(logging.DEBUG)

# Connection
RethinkConnection()
# Query main object
query = RDBquery()
# Elasticsearch object
es = Elasticsearch(**ES_SERVICE)

_cache = {}
transcrpcache = []
u = Utils()


def add_suggestion(key, value, probability=1, extra=None, is_extrait=False):
    """
    Add to suggestion only if not available already
    """

    # Handle empty
    if value is None:
        return False
    else:
        original = value

    # 1. lower?
    value = value.lower()
    # 2. strip quotes?
    value.strip('"')
    # 3. split on any symbols and take the biggest word? 
    if is_extrait:
        pass
    elif not value.isalpha():

        max_len = 0
        # myword = None
        for word in re.split(r'[^a-z]+', value):
            cur_len = len(word)
            if cur_len > max_len:
                max_len = cur_len
                # myword = word
                value = word

        # print("TEST!", original, myword)
        # import time
        # time.sleep(3)

    # Handle cache
    if key not in _cache:
        _cache[key] = {}
    if value in _cache[key]:
        # print("Skipping")
        return False

    # 4. check length
    value_len = len(value)

    if value_len > 3:
        if extra is None:
            extra = {'cleanlabel': key}

        body = {
            SUGGEST: value,
            'original': original,
            'label': key,
            'prob': probability,
            'extra': extra
        }

        # ADD
        es.index(index=EL_INDEX2, doc_type=EL_TYPE2, body=body)

    _cache[key][value] = True
    # cache also with ending s?
    last_char = value_len - 1
    if value[last_char] in 'aeiou':
        _cache[key][value + 's'] = True

    # print("Suggest adding", key, value, probability)
    return True


def suggest_transcription(transcription, key, probability=0.5, extrait=None):

    if transcription is None or transcription.strip() == '':
        return False

    if transcription in transcrpcache:
        # logger.debug("Suggestion already cached")
        return False

    # print("Suggest ", key)
    transcrpcache.append(transcription)
    # if '[Non transcrit]' in transcription:
    #     return False

    words = es.indices.analyze(
        index=EL_INDEX0, analyzer='my_html_analyzer', body=transcription)

    for token in words['tokens']:
        for word in token['token'].split("'"):
            token['cleanlabel'] = key.split('_')[0]

            if len(word) > 2:

                # if 'scytalosagittipelliger' in word:
                #     print("TEST", extrait, word.encode())
                #     # exit(1)

                add_suggestion(key, word, probability, extra=token)
    return True


def read_xls():

    # NEW
    from .gxls import GExReader
    obj = GExReader(rethink=query, elastic=es)
    obj.get_data()

    # # OLD
    # from .xls import ExReader
    # obj = ExReader(rethink=query, elastic=es)
    # if obj.check_empty():
    #     raise BaseException("Failed to load 'Lexique'")
    # return obj.get_data()


def single_update(doc):
    """ elastic search SINGLE ELEMENT insert/update """

    record = doc['record']
    # print(doc)

    # if record in toberemoved:
    #     q.get(record).delete().run()
    #     logger.info("Removed useless %s" % record)
    #     continue

    elobj = {}
    not_valid = False

    date = {}
    for step in doc['steps']:

        ###################
        # Single step
        current_step = int(step['step'])
        if not_valid:
            break
        value = None
        key = None

        #############################
        # Add extra search elements
        for element in step['data']:
            pos = element['position']
            extrakey = None
            # print("Current step", current_step, pos)
            if pos == 1:
                value = element['value']
                # break

            if 'value' in element and len(element['value']) > 0:
                if current_step == 1:
                    if pos == 2:
                        extrakey = 'page'
                    if pos == 3:
                        # element['value'] = False
                        extrakey = 'gravure'
                        if 'gravure' in element['value'].lower():
                            element['value'] = True
                            # print("FOUND!\n\n")
                        else:
                            element['value'] = False
                    # if pos == 5:
                    #     print("TEST!\n\n", element)
                    #     exit(1)
                    #     extrakey = 'gravure'
                if current_step == 2:
                    if pos == 2:
                        extrakey = 'manuscrit'
                elif current_step == 3:
                    if pos == 4:
                        # extrakey = 'date'
                        date['year'] = int(element['value'])
                    elif pos == 5:
                        extrakey = 'lieu'
                    elif pos == 8:
                        date['start'] = element['value']
                    elif pos == 9:
                        date['end'] = element['value']
                    # elif pos > 9:
                    #     if len(date) < 1:
                    #         pp(elobj)
                    #         time.sleep(5)
                elif current_step == 4:
                    if pos == 6:
                        extrakey = 'apparato'
                    elif pos == 4:
                        extrakey = 'actions'
                    elif pos == 3:
                        extrakey = 'temps'

                if extrakey is not None:
                    # print("TEST", extrakey, "*" + element['value'] + "*")
                        elobj[extrakey] = element['value']

        #############################
        if current_step == 1:
            if value is None:
                logger.error("Invalid element %s" % record)
                # # print("ID", record, step)
                # q.get(record).delete().run()
                # logger.warn("Element '%s' invalid... Removed")
                # not_valid = True
                # break
                exit(1)

            # if 'Paler' in value:
            #     if 'idea' in value:
            #         if '39' in value:
            #             pass
            #         else:
            #             return
            #     else:
            #         return
            # else:
            #     return
            # https://stackoverflow.com/a/34378962

            key = 'extrait'
            try:
                ##########################
                # sorting stuff

                # TO FIX: Sort is a problem in baroque
                elobj['sort_number'], prob, elobj['extrait_number'] = \
                    u.get_page(value.strip())
                # exit(1)

                ##########################
                # # WRONG SORT BY PAGE
                # print(elobj)
                # group = u.group_extrait(elobj['page'])
                # elobj['sort_string'] = group[0]
                # num, prob = u.get_numeric_extrait(group)
                # elobj['sort_number'] = u.get_sort_value(value, num)

                ##########################
                # Suggest EXTRAIT

                # Forget about numbers in that case
                suggest_value = re.sub(
                    r'_[0-9]+', '',
                    value)

                if '_' in suggest_value:
                    if suggest_value.endswith('_MS'):
                        pass
                    else:
                        suggest_value = suggest_value.replace('_', '_*_')
                else:
                    suggest_value += '_'
                    if ' ' in suggest_value:
                        suggest_value = '"%s"' % suggest_value
                # print("TEST ME", suggest_value)
                add_suggestion(key, suggest_value, prob, is_extrait=True)

            except Exception as e:
                print("VALUES WAS", value, step)
                raise e

        elif current_step == 2:
            key = 'source'
            # add_suggestion(key, value, .9)

        elif current_step == 3:
            key = 'fete'
            # add_suggestion(key, value, .7)
            # if value == 'prova':
            #     print("STOP!")
            #     pp(record)
            #     exit(1)
            logger.debug(value)

        if key is not None and value is not None:
            elobj[key] = value

    ###################
    # Transcriptions and translations

    key = 'transcription'
    if key in elobj:
        elobj.pop(key)
    if not not_valid and ('fete' not in elobj or 'extrait' not in elobj):
        logger.warning("Invalid object %s" % elobj)
        return

    # Update with data from the images and translations + transcriptions
    exist = query.get_table_query(RDB_TABLE2) \
        .get_all(record).count().run()

    if exist:
        docobj = {}
        doc_cursor = query.get_table_query(RDB_TABLE2) \
            .get_all(record).run()
        data = list(doc_cursor).pop(0)
        image = data['images'].pop(0)
        # print(image)

        langue = ''

        # TRANSCRIPT
        if "transcriptions" in image and len(image["transcriptions"]) > 0:
            logger.debug("Found transcription")
            key = 'transcription'
            if 'language' in image:
                # key += '_' + image['language'].lower()
                langue = image['language']

            transcription = image["transcriptions"].pop(0)
            suggest_transcription(transcription, key, .25, elobj['extrait'])
            if 'language' in image:
                key += '_' + image['language'].lower()
            docobj[key] = transcription

        # TRANSLATE
        if "translations" in image and len(image["translations"]) > 0:

            for language, translation in image["translations"].items():
                key = 'traduction'
                suggest_transcription(transcription, key, .20, elobj['extrait'])

                key = 'traduction_' + language.lower()
                logger.debug("Found translations: %s" % language)
                # suggest_transcription(transcription, key, .20)
                docobj[key] = translation
                langue += ' ' + language

        docobj['thumbnail'] = ZoomEnabling.get_thumbname(image['filename'])
        elobj['doc'] = docobj
        elobj['langue'] = langue.lower()

        # es.update(
        #     index=EL_INDEX1, id=record,
        #     body={"doc": docobj}, doc_type=EL_TYPE1)

    else:
        noimages[elobj['extrait']] = elobj

    ###################
    ## Date format

    # Input date(year, start, end)
    if len(date) > 0:
        objdate = {
            'years': {'start': None, 'end': None},
            'months': {'start': None, 'end': None},
            'days': {'start': None, 'end': None}
        }

        if 'year' in date:

            # Iso format
            if 'start' not in date:
                x = datetime.datetime(
                    year=date['year'], month=1, day=1).isoformat()
                elobj['start_date'] = x + '.000Z'
            if 'end' not in date:
                x = datetime.datetime(
                    year=date['year'], month=12, day=31).isoformat()
                elobj['end_date'] = x + '.000Z'

            # String representation
            tmp = str(date['year'])
            objdate['years']['start'] = tmp
            objdate['years']['end'] = tmp

        if 'start' in date:
            elobj['start_date'] = date['start']
            objdate = set_date_period(date, objdate, code='start')

        if 'end' in date:
            elobj['end_date'] = date['end']
            objdate = set_date_period(date, objdate, code='end')

        # build the date string to show inside the search like
        # 1622 / 03-04 / 11-19
        newyear = str(objdate['years']['start'])
        if objdate['years']['end'] != objdate['years']['start']:
            newyear += '-' + str(objdate['years']['end'])

        newmonth = ''
        if objdate['months']['start'] is not None:
            newmonth = str(objdate['months']['start']).zfill(2)
        if objdate['months']['end'] is not None:
            if objdate['months']['end'] != objdate['months']['start']:
                if newmonth != '':
                    newmonth += '-'
                newmonth += str(objdate['months']['end']).zfill(2)
        if newmonth != '':
            newmonth += ' / '

        newday = ''
        if objdate['days']['start'] is not None:
            newday = str(objdate['days']['start']).zfill(2)
        if objdate['days']['end'] is not None:
            if objdate['days']['end'] != objdate['days']['start']:
                if newday != '':
                    newday += '-'
                newday += str(objdate['days']['end']).zfill(2)
        if newday != '':
            newday += ' / '

        elobj['date'] = newday + newmonth + newyear

    else:
        print("FAIL", doc['steps'][2])
        exit(1)

    ###################
    # save
    es.index(index=EL_INDEX1, id=record, body=elobj, doc_type=EL_TYPE1)
    print("")
    return elobj


#################################
# MAIN
#################################
def make(only_xls=False, skip_lexique=False):

    ###################
    if not only_xls:

        q = query.get_table_query(RDB_TABLE1)
        cursor = q.run()
        # print("SOME", cursor)

        # HTML STRIPPER
        if es.indices.exists(index=EL_INDEX0):
            es.indices.delete(index=EL_INDEX0)
        es.indices.create(index=EL_INDEX0, body=HTML_ANALYZER)

        # MULTI INDEX FILTERING
        if es.indices.exists(index=EL_INDEX1):
            es.indices.delete(index=EL_INDEX1)
        es.indices.create(index=EL_INDEX1, body=INDEX_BODY1)
        logger.info("Created index %s" % EL_INDEX1)

        # SUGGESTIONS
        if es.indices.exists(index=EL_INDEX2):
            es.indices.delete(index=EL_INDEX2)
        es.indices.create(index=EL_INDEX2, body=INDEX_BODY2)
        logger.info("Created index %s" % EL_INDEX2)

        # es.indices.put_mapping(
        #     index=EL_INDEX2, doc_type=EL_TYPE2, body=SUGGEST_MAPPINGS)
        # print(es.indices.stats(index=EL_INDEX2))
        # exit(1)

        # print(es.indices.stats(index=EL_INDEX1))
        # print(es.info())

    ##################
    # LEXIQUE
    if not skip_lexique:

        if es.indices.exists(index=EL_INDEX3):
            es.indices.delete(index=EL_INDEX3)
        es.indices.create(index=EL_INDEX3, body={})
        logger.info("Created index %s" % EL_INDEX3)

        # READ FROM XLS FILE
        read_xls()
        # dictionary = read_xls(fix_suggest=(not only_xls))

        if only_xls:
            return False

    ###################
    count = 0
    for doc in cursor:
        elobj = single_update(doc)
        if elobj is not None:
            count += 1
            logger.info("[Count %s]\t%s" % (count, elobj['extrait']))

    # print("TOTAL", es.search(index=EL_INDEX1))
    print("Completed. No images:")
    pp(noimages.keys())
    return True
