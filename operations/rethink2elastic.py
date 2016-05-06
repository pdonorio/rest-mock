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

fields = ['extrait', 'source', 'fete', 'transcription', 'date', 'place']

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
                "fete": {"type": "string"},
                "transcription": {"type": "string"},
                "sort_string": {
                    "type": "string",
                    "include_in_all": False
                },
                "sort_number": {
                    "type": "integer",
                    "include_in_all": False
                },
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
                "place": {
                    "type": "string",
                    "index": "no",
                    "include_in_all": False
                },
            }
        }
    }
}

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


# Connection
RethinkConnection()
# Query main object
query = RDBquery()
# Elasticsearch object
es = Elasticsearch(**ES_SERVICE)


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
  }

    """

    cursor = query.get_table_query(RDB_TABLE1).run()
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

            if not_valid:
                break
            value = None
            key = None
            for element in step['data']:
                if element['position'] == 1:
                    value = element['value']
                    # break
                elif step['step'] == 3 and element['position'] == 4:
                    elobj['date'] = element['value']
                elif step['step'] == 3 and element['position'] == 5:
                    elobj['place'] = element['value']

            if step['step'] == 1:
                if value is None:
                    logger.warn("Element is not valid")
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
                    es.index(index=EL_INDEX2, doc_type=EL_TYPE2, body={
                        'label': key, 'suggest': value, 'prob': prob})
                    elobj['sort_number'] = num
                except Exception as e:
                    print("VALUES WAS", value, step)
                    raise e

            elif step['step'] == 2:
                key = 'source'
                # suggest
                if value is not None:
                    out = es.search(
                        index=EL_INDEX2,
                        body={'query': {'match': {'suggest': value}}})
                    if out['hits']['total'] < 1:
                        es.index(
                            index=EL_INDEX2, doc_type=EL_TYPE2,
                            body={'label': key, 'suggest': value, 'prob': .9})

            elif step['step'] == 3:
                key = 'fete'
                # suggest
                if value is not None:
                    out = es.search(
                        index=EL_INDEX2,
                        body={'query': {'match': {'suggest': value}}})
                    if out['hits']['total'] < 1:
                        es.index(
                            index=EL_INDEX2, doc_type=EL_TYPE2,
                            body={'label': key, 'suggest': value, 'prob': .7})

            if key is not None and value is not None:
                elobj[key] = value

        # print("object", record, elobj)
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

            if "transcriptions" in image and len(image["transcriptions"]) > 0:

                key = 'transcription'
                trans = image["transcriptions"].pop(0)

                words = es.indices.analyze(
                    index=EL_INDEX0, analyzer='my_html_analyzer', body=trans)
                for token in words['tokens']:
                    word = token['token']
                    if len(word) > 3:
                        # out = es.search(
                        #     index=EL_INDEX2,
                        #     body={'query': {'match': {'suggest': word}}})
                        # if out['hits']['total'] < 1:
                        es.index(index=EL_INDEX2, doc_type=EL_TYPE2,
                                 body={'label': key, 'suggest': word,
                                       'prob': .25, 'extra': token})
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
