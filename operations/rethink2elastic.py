# -*- coding: utf-8 -*-

from __future__ import absolute_import

from restapi.resources.services.rethink import RethinkConnection, RDBquery
# from restapi.resources.custom.docs import image_destination
# from rethinkdb import r
from restapi.resources.services.elastic import \
    BASE_SETTINGS, ES_SERVICE, HTML_ANALYZER, \
    EL_INDEX0, EL_INDEX1, EL_INDEX2, EL_TYPE1, EL_TYPE2
from elasticsearch import Elasticsearch

from restapi import get_logger
import re
import logging

logger = get_logger(__name__)
logger.setLevel(logging.DEBUG)

RDB_TABLE1 = "datavalues"
RDB_TABLE2 = "datadocs"

fields = [
    'extrait', 'source', 'fete',
    'transcription', 'traduction',
    'date', 'lieu', 'manuscrit'
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
                    # "index": "not_analyzed"
                },
                "source": {"type": "string"},
                "fete": {
                    "type": "string",
                # UHM
                    "index": "not_analyzed"
# https://www.elastic.co/guide/en/elasticsearch/reference/current/multi-fields.html
                    # Multi analyzer for this field
                    # "fields": {
                    #     "prova": {
                    #         "type": "string",
                    #         "index": "not_analyzed"
                    #     },
                    #     "test": {
                    #         "type": "string",
                    #     }
                    # }
                },

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

                "date": {
                    "type": "string",
                    "index": "no",
                    "include_in_all": False
                },
                "lieu": {
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

# Connection
RethinkConnection()
# Query main object
query = RDBquery()
# Elasticsearch object
es = Elasticsearch(**ES_SERVICE)

_cache = {}


def add_suggestion(key, value, probability=1, extra=None):
    """
    Add to suggestion only if not available already
    """
    if value is None:
        return False

    if key not in _cache:
        _cache[key] = {}

    # Check if suggestion is already there
    # if extra is None:
    #     out = es.search(
    #         index=EL_INDEX2, body={'query': {'match': {SUGGEST: value}}})
    #     # If no hits, add this
    #     if out['hits']['total'] > 0:
    #         return False
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


#################################
# MAIN
#################################
def make():
    """
    Elastic

  {
    id @record
    extrait
    source
    fete
    transcription @update
    image_thumbnail_path @update

## TO FIX: add vocabulary?

  }

    """

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
    for doc in cursor:
        # print(doc)
        record = doc['record']

# NORMAL INSERT
        elobj = {}
        not_valid = False

        for step in doc['steps']:

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
                elif current_step == 2:
                    if pos == 2:
                        extrakey = 'manuscrit'
                elif current_step == 3:
                    if pos == 4:
                        extrakey = 'date'
                    elif pos == 5:
                        extrakey = 'lieu'

                if extrakey is not None and element['value'].strip() != '':
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

                    # Divide the value
                    pattern = re.compile(r'^([^0-9]+)([\_0-9]+)([^\_]*)')
                    m = pattern.match(value)
                    if m:
                        g = m.groups()
                    else:
                        g = ('Z', '_99999_')

                    elobj['sort_string'] = g[0]

                    num = int(g[1].replace('_', ''))
                    if num < 2:
                        prob = 2.5
                    else:
                        prob = .5 - (num / 250)

                    # suggest
                    add_suggestion(key, value, prob)
                    elobj['sort_number'] = num
                except Exception as e:
                    print("VALUES WAS", value, step)
                    raise e

            elif current_step == 2:
                key = 'source'
                # add_suggestion(key, value, .9)

            elif current_step == 3:
                key = 'fete'
                # add_suggestion(key, value, .7)
                logger.debug(value)

            if key is not None and value is not None:
                elobj[key] = value

        # print("object", record, elobj)
        # exit(1)

        # CHECK
        key = 'transcription'
        if key in elobj:
            elobj.pop(key)

        if not not_valid and 'fete' not in elobj:
            logger.warning("Invalid object", elobj)
            continue
            # exit(1)

        es.index(index=EL_INDEX1, id=record, body=elobj, doc_type=EL_TYPE1)
        print("Index count", count)

        count += 1

        # NORMAL UPDATE
        exist = query.get_table_query(RDB_TABLE2) \
            .get_all(record).count().run()

        if exist:
            elobj = {}
            doc_cursor = query.get_table_query(RDB_TABLE2) \
                .get_all(record).run()
            data = list(doc_cursor).pop(0)
            image = data['images'].pop(0)
            # print(image)

            if "transcriptions" in image and len(image["transcriptions"]) > 0:

                logger.debug("Found transcription")
                key = 'transcription'
                trans = image["transcriptions"].pop(0)

                if trans.strip() != '':
                    words = es.indices.analyze(
                        index=EL_INDEX0, analyzer='my_html_analyzer',
                        body=trans)
                    for token in words['tokens']:
                        word = token['token']
                        if len(word) > 3:
                            add_suggestion(key, word, .25, extra=token)

                    elobj[key] = trans

            if "translations" in image and len(image["translations"]) > 0:

                for language, trans in image["translations"].items():
                    key = 'translation_' + language.lower()
                    logger.debug("Found translations: %s" % language)

                    if trans.strip() != '':
                        words = es.indices.analyze(
                            index=EL_INDEX0, analyzer='my_html_analyzer',
                            body=trans)
                        # print("Translate", words);import time; time.sleep(2)
                        for token in words['tokens']:
                            word = token['token']
                            if len(word) > 3:
                                add_suggestion(key, word, .25, extra=token)

                        elobj[key] = trans

            f = image['filename']
            elobj['thumbnail'] = '/static/uploads/' + \
                f[:f.index('.', len(f) - 5)] + \
                '/TileGroup0/0-0-0.jpg'
            # print(elobj)

            es.update(
                index=EL_INDEX1, id=record,
                body={"doc": elobj}, doc_type=EL_TYPE1)

    # print("TOTAL", es.search(index=EL_INDEX1))

    print("Completed")
