# -*- coding: utf-8 -*-

from restapi.resources.services.rethink import RethinkConnection, RDBquery
from restapi.resources.services.uploader import ZoomEnabling
from restapi.resources.services.elastic import \
    BASE_SETTINGS, ES_SERVICE, \
    HTML_ANALYZER, EL_INDEX0, EL_INDEX1, EL_INDEX2, EL_TYPE1, EL_TYPE2

from elasticsearch import Elasticsearch
from restapi import get_logger
from beeprint import pp
import logging
import datetime
from restapi.dates import set_date_period
from restapi.commons.conversions import Utils


RDB_TABLE1 = "datavalues"
RDB_TABLE2 = "datadocs"
toberemoved = [
    'd2d5fcb6-81cc-4654-9f65-a436f0780c67'  # prova
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

                "sort_string": {
                    "type": "string",
                    "include_in_all": False
                },
                "sort_number": {
                    "type": "integer",
                    "include_in_all": False
                },

                "transcription": {"type": "string"},
                "traduction": {"type": "string"},
                "thumbnail": {
                    "type": "string",
                    "index": "no",
                    "include_in_all": False
                },
            }
        }
    }
}

# INDEX 2 is SUGGESTIONs

INDEX_BODY2 = {
    'settings': BASE_SETTINGS,
    'mappings': {
        EL_INDEX2: {
            'properties': {
                "suggest": {
                    "type": "string",
                    "analyzer": "nGram_analyzer"
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


def add_suggestion(key, value, probability=1, extra=None):
    """
    Add to suggestion only if not available already
    """
    if value is None:
        return False

# // TO FIX:
# split on symbols and take the biggest word?

    if key not in _cache:
        _cache[key] = {}

    # Check if suggestion is already there
    # if extra is None:
    #     out = es.search(
    #         index=EL_INDEX2, body={'query': {'match': {SUGGEST: value}}})
    #     # If no hits, add this
    #     if out['hits']['total'] > 0:
    #         return False

    if extra is None:
        extra = {'cleanlabel': key}

    if value in _cache[key]:
        # print("Skipping")
        return False

    body = {'label': key, SUGGEST: value, 'prob': probability}
    if extra is not None:
        body['extra'] = extra

    # ADD
    es.index(index=EL_INDEX2, doc_type=EL_TYPE2, body=body)
    _cache[key][value] = True

    # print("Suggest adding", key, value, probability)
    return True


def suggest_transcription(transcription, key, probability=0.5):

    if transcription.strip() == '':
        return False

    if transcription in transcrpcache:
        logger.debug("Suggestion already cached")
        return False

    # print("Suggest ", key)
    transcrpcache.append(transcription)

    words = es.indices.analyze(
        index=EL_INDEX0, analyzer='my_html_analyzer', body=transcription)

    for token in words['tokens']:
        word = token['token']
        token['cleanlabel'] = key.split('_')[0]
        if len(word) > 3:
            add_suggestion(key, word, probability, extra=token)
    return True

def read_xls(fix_suggest=False):
    print("FIX SUGGEST", fix_suggest)
    from .xls import ExReader
    obj = ExReader(rethink=query, elastic=None)
    if obj.check_empty():
        raise BaseException("Failed to load 'Lexique'")
    return obj.get_data()

#################################
# MAIN
#################################
def make(only_xls=False):

######################
# TO BE REMOVED
    dictionary = read_xls(fix_suggest=(not only_xls))
    print("DEBUG"); exit(1)
# TO BE REMOVED
######################

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

    # SUGGESTIONS
    if es.indices.exists(index=EL_INDEX2):
        es.indices.delete(index=EL_INDEX2)
    es.indices.create(index=EL_INDEX2, body=INDEX_BODY2)
    # es.indices.put_mapping(
    #     index=EL_INDEX2, doc_type=EL_TYPE2, body=SUGGEST_MAPPINGS)
    # print(es.indices.stats(index=EL_INDEX2))
    # exit(1)

    # print(es.indices.stats(index=EL_INDEX1))
    # print(es.info())

    # MAIN CYCLE on single document
    count = 0
    noimages = {}
    for doc in cursor:
## SINGLE STEP
## TO MOVE SOMEWHERE ELSE and use it when a new record is created!

        # print(doc)
        record = doc['record']
        if record in toberemoved:
            q.get(record).delete().run()
            logger.info("Removed useless %s" % record)
            continue

        elobj = {}
        not_valid = False

        date = {}
        for step in doc['steps']:

            current_step = int(step['step'])
            # if current_step == 3:
            #     pp(step)
            #     exit(1)
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
                    # print("ID", record, step)
                    q.get(record).delete().run()
                    logger.warn("Element '%s' invalid... Removed")
                    not_valid = True
                    break

                key = 'extrait'
                try:
                    # sorting stuff
                    group = u.group_extrait(elobj['page'])
                    elobj['sort_string'] = group[0]
                    num, prob = u.get_numeric_extrait(group)
                    elobj['sort_number'] = u.get_sort_value(value, num)
                    # suggest
                    add_suggestion(key, value, prob)

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

        ###############################
        # # print("object", record, elobj)
        # # exit(1)
        # if 'apparato' in elobj:
        #     pp(elobj)
        #     time.sleep(3)

        # CHECK
        key = 'transcription'
        if key in elobj:
            elobj.pop(key)

        if not not_valid and ('fete' not in elobj or 'extrait' not in elobj):
            logger.warning("Invalid object %s" % elobj)
            continue

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

            # TRANSCRIPT
            if "transcriptions" in image and len(image["transcriptions"]) > 0:
                logger.debug("Found transcription")
                key = 'transcription'
                if 'language' in image:
                    key += '_' + image['language'].lower()

                transcription = image["transcriptions"].pop(0)
                suggest_transcription(transcription, key, .25)
                docobj[key] = transcription

            # TRANSLATE
            if "translations" in image and len(image["translations"]) > 0:

                for language, translation in image["translations"].items():
                    key = 'traduction_' + language.lower()
                    logger.debug("Found translations: %s" % language)
                    suggest_transcription(transcription, key, .20)
                    docobj[key] = translation

            docobj['thumbnail'] = ZoomEnabling.get_thumbname(image['filename'])
            elobj['doc'] = docobj

            # es.update(
            #     index=EL_INDEX1, id=record,
            #     body={"doc": docobj}, doc_type=EL_TYPE1)

        else:
            noimages[elobj['extrait']] = elobj

        # Insert the elasticsearch document!
        count += 1
        logger.info("[Count %s]\t%s" % (count, elobj['extrait']))

        # pp(elobj)
        # time.sleep(5)

############################
############################

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
############################
############################

        es.index(index=EL_INDEX1, id=record, body=elobj, doc_type=EL_TYPE1)
        print("")

    # print("TOTAL", es.search(index=EL_INDEX1))
    print("Completed")
    pp(noimages.keys())
