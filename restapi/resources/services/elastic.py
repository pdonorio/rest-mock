# -*- coding: utf-8 -*-

""" Being fast at searching """

from elasticsearch import Elasticsearch
from ... import get_logger

logger = get_logger(__name__)

ES_SERVER = 'el'
ES_SERVICE = {"host": ES_SERVER, "port": 9200}
EL_INDEX0 = "split_html"
EL_INDEX1 = "catalogue"
EL_INDEX2 = "suggestions"
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

    def get_instance(self):
        self._api = Elasticsearch(**ES_SERVICE)
        logger.info("Connected to Elasticsearch")
        return self

    def fast_get(self, keyword):  # , fields=[]):

        args = {'index': EL_INDEX1, 'doc_type': EL_TYPE1}

        # if id is not None:
        #     args['id'] = id
        #     return self._api.get(**args)
        # else:

        if keyword is not None:
            args['body'] = {
                'query': {"match": {"_all": {"query": keyword}}}
            }

        args['sort'] = ["sort_string:asc", "sort_number:asc"]

        out = self._api.search(**args)
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