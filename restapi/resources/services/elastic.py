# -*- coding: utf-8 -*-

""" Being fast at searching """

from elasticsearch import Elasticsearch
from ... import get_logger

logger = get_logger(__name__)

SERVER = 'el'
EL_INDEX1 = 'autocomplete'
EL_TYPE1 = 'data'


# ######################################
#
# # Elasticsearch class wrapper
#
# ######################################
class FastSearch(object):

    def get_instance(self):
        self._api = Elasticsearch(host=SERVER)
        logger.info("Connected to Elasticsearch")
        return self

    def fast_get(self, id):
        args = {'index': EL_INDEX1, 'doc_type': EL_TYPE1}
        if id is not None:
            args['id'] = id
            return self._api.get(**args)
        else:
            out = self._api.search(**args)
            return out['hits']['hits']
