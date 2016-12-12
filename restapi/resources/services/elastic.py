# -*- coding: utf-8 -*-

"""
Being fast at searching

distinct = aggregations

conn = connections.Elasticsearch(host='el')
# a = A('terms', field='fete')
a = A('terms', field='fete.raw', size=0)
s = Search(using=conn, index='catalogue')
s.aggs.bucket('fete_terms', a)
response = s.execute()
response.aggregations.fete_terms.to_dict()

http://elasticsearch-dsl.readthedocs.io/en/latest/search_dsl.html?highlight=aggregation

"""

from elasticsearch import Elasticsearch
from beeprint import pp
from ... import get_logger

logger = get_logger(__name__)

ES_SERVER = 'el'
ES_SERVICE = {"host": ES_SERVER, "port": 9200}
EL_INDEX0 = "split_html"
EL_INDEX1 = "catalogue"
EL_INDEX2 = "suggestions"
EL_INDEX3 = "lexique"
# EL_INDEX2 = "distinct"
EL_TYPE1 = 'data'
EL_TYPE2 = 'words'

#################################
# Elastic search base settings
# From: http://j.mp/1pRKBCs
BASE_SETTINGS = {
    "analysis": {
        "filter": {
            "nGram_filter": {
                "type": "nGram",
                "min_gram": 1,
                "max_gram": 20,
                "token_chars": [
                    "letter",
                    "digit",
                    "punctuation",
                    "symbol"
                ]
            }
        },
        "analyzer": {
            "nGram_analyzer": {
                "type": "custom",
                "tokenizer": "whitespace",
                "filter": [
                    "lowercase",
                    "asciifolding",
                    "nGram_filter"
                ]
            },
            "whitespace_analyzer": {
                "type": "custom",
                "tokenizer": "whitespace",
                "filter": [
                    "lowercase",
                    "asciifolding"
                ]
            }
        }
    }
}

HTML_ANALYZER = {
    "settings": {
        "analysis": {
            "analyzer": {
                "my_html_analyzer": {
                    "tokenizer": "standard",
                    "char_filter": ["html_strip"]
                }
            }
        }
    }
}


# ######################################
#
# # Elasticsearch class wrapper
#
# ######################################
class FastSearch(object):
    """
    A simple class to make important operations on full text search
    """

    def get_instance(self):
        self._api = Elasticsearch(**ES_SERVICE)
        logger.info("Connected to Elasticsearch")
        try:
            self._api.ping()
        except Exception as e:
            logger.critical("Elasticsearch connection failed:\n'%s'" % e)
            return False
        return self

    def fast_query(self, field, value):

        if not self.get_instance():
            return []

        args = {'index': EL_INDEX1, 'doc_type': EL_TYPE1, 'size': 10000}
        args['body'] = {"query": {"bool": {"must": [
                        {"term": {field: {"value": value}}}]}}}
        try:
            out = self._api.search(**args)
        except Exception as e:
            logger.error("Failed to execute fast get query\n%s" % e)
            return None, False
        # pp(out)
        return out['hits']['hits']

    def fast_get_all(self, keyword, size=5, index=EL_INDEX3, type=EL_TYPE1):

        args = {'index': index, 'doc_type': type}
        # args['sort'] = ["sort_string:asc", "sort_number:asc"]
        # args['from_'] = current - 1
        args['from_'] = 0
        args['size'] = size
        args['body'] = {
            'query': {"match": {"_all": {"query": keyword}}}
        }

        try:
            out = self._api.search(**args)
        except Exception as e:
            logger.error("Failed to execute fast get query\n%s" % e)
            return None, False
        pp(out)
        return out['hits']['hits'], out['hits']['total']

    def fast_get(self, keyword, current=1, size=10, filters={}):

        args = {'index': EL_INDEX1, 'doc_type': EL_TYPE1}
        args['sort'] = ["sort_string:asc", "sort_number:asc"]
        args['from_'] = current - 1
        args['size'] = size

        if keyword is not None or len(filters) > 0:
            args['body'] = {
                # 'query': {"match": {"_all": {"query": keyword}}}

                # http://stackoverflow.com/a/15528305/2114395
                'query': {
                    'filtered': {
                    }
                }
            }

            if keyword is not None:
                args['body']['query']['filtered']['query'] = {
                    "query_string": {
                        "query": keyword
                    }
                }
            if len(filters) > 0:
                musts = []
                for key, value in filters.items():
                    # Normal string query
                    if '_date' not in key:
                        musts.append({'term': {key: value}})
                    # DATE string query
                    else:
                        compare = None
                        mydateformat = "yyyy||MM-yyyy||dd-MM-yyyy"
                        if key.startswith('start'):
                            compare = 'gte'
                            key = 'end_date'
                        elif key.startswith('end'):
                            compare = 'lte'
                            key = 'start_date'
                        if len(value) == 4:
                            value += '||/y'
                        elif len(value) == 7:
                            value += '||/M'
                        elif len(value) == 10:
                            value += '||/d'
                        musts.append({'range': {key: {
                            compare: value,
                            "format": mydateformat
                        }}})
                args['body']['query']['filtered']['filter'] = {
                    "bool": {
                        "must": musts
                    }
                }

        # pp(args)

        try:
            out = self._api.search(**args)
        except Exception as e:
            logger.error("Failed to execute fast get query\n%s" % e)
            return None, False
        # print(out)
        return out['hits']['hits'], out['hits']['total']

    def fast_suggest(self, text):

        if text is None or text.strip() == '':
            return []

        obj = {"query": {
            "function_score": {
                "query": {
                    "filtered": {
                        "query": {'match': {'suggest': text}}
                    }
                },
                "min_score": 30,
                "functions": [
                    {"script_score": {"script": "_score * doc['prob'].value"}}
                ]
            }}}
        args = {'index': EL_INDEX2, 'body': obj}
        out = self._api.search(**args)
        # print("TEST", out)
        return out['hits']['hits']

    def fast_update(self, id, data, image=False):

        if not self.get_instance():
            return False

        if image:
            from ..services.uploader import Uploader
            data = {'doc': {'thumbnail': Uploader.get_thumbname(data)}}

        args = {
            'id': id, 'body': {'doc': data},
            'index': EL_INDEX1, 'doc_type': EL_TYPE1,
        }

        try:
            self._api.update(**args)
            logger.info("Updated search %s" % id)
        except Exception as e:
            logger.error("Failed to execute fast update %s\n%s" % (id, e))
            return False

        return True

    def fast_remove(self, id):

        if not self.get_instance():
            return False

        args = {
            'id': id,
            'index': EL_INDEX1,
            'doc_type': EL_TYPE1,
        }

        try:
            self._api.delete(**args)
        except Exception as e:
            logger.error("Failed to execute fast delete %s\n%s" % (id, e))
            return False

        return True
