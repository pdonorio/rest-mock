#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" REST API Resources package """

import logging
logger = logging.getLogger(__name__)

from mylibs.meta import Meta
FIXED_APIURL = '/api' + '/'

def create_endpoint(rest_api, resource, endpoint, endkey):

    address = FIXED_APIURL + endpoint
    logger.info("Adding '%s' resource to REST address: *%s*", \
        resource.__name__, address)

    # Create restful endpoint
    rest_api.add_resource(resource, \
        FIXED_APIURL+endpoint,\
        FIXED_APIURL + endpoint +'/<'+ endkey +'>')

def create_endpoints(rest_api, module):
    """ Automatic creation of endpoint from specified resources """

    resources = Meta().get_new_classes_from_module(module)
    # Init restful plugin
    if len(resources) > 0:
        # For each RESTful resource i receive
        for resource in resources:
            endpoint, endkey = resource().get_endpoint()
            create_endpoint(rest_api, resource, endpoint, endkey)
