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
        try:
            self._api.ping()
        except Exception as e:
            logger.critical("Elasticsearch connection failed:\n'%s'" % e)
            return False
        return self

    def fast_get(self, keyword, current=1, size=10):

        args = {'index': EL_INDEX1, 'doc_type': EL_TYPE1}
        args['sort'] = ["sort_string:asc", "sort_number:asc"]
        args['from_'] = current - 1
        args['size'] = size

        if keyword is not None:
            args['body'] = {
                'query': {"match": {"_all": {"query": keyword}}}
            }

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
