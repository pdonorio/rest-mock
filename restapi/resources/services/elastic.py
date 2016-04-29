# -*- coding: utf-8 -*-

""" Being fast at searching """

from elasticsearch import Elasticsearch
from ... import get_logger

logger = get_logger(__name__)
SERVER = 'el'


# ######################################
#
# # Elasticsearch class wrapper
#
# ######################################
class FastSearch(object):

    def get_instance(self):
        self._api = Elasticsearch(host=SERVER)
        return self
