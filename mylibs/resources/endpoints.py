#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" How to create endpoints into REST service """

from mylibs import get_logger
logger = get_logger(__name__)

from mylibs.meta import Meta
from mylibs.resources import FIXED_APIURL

class Endpoints(object):
    """ Handling endpoints creation"""

    rest_api = None

    def __init__(self, api):
        super(Endpoints, self).__init__()
        self.rest_api = api

    def create_single(self, resource, endpoint, endkey):
        """ Adding a single restpoint from a Resource Class """

        address = FIXED_APIURL + endpoint
        logger.info("Adding '%s' resource to REST address: *%s*", \
            resource.__name__, address)

        # Create restful endpoint
        self.rest_api.add_resource(resource, \
            FIXED_APIURL+endpoint,\
            FIXED_APIURL + endpoint +'/<'+ endkey +'>')

    def many_from_module(self, module):
        """ Automatic creation of endpoint from specified resources """

        resources = Meta().get_new_classes_from_module(module)
        # Init restful plugin
        if len(resources) > 0:
            # For each RESTful resource i receive
            for resource in resources:
                endpoint, endkey = resource().get_endpoint()
                self.create_single(resource, endpoint, endkey)
