#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" REST API Resources package """

FIXED_APIURL = '/api' + '/'

from flask_restful import Api
from mylibs.meta import Meta

import logging
logger = logging.getLogger()

def create_endpoints(module, microservice):
    """ Automatic creation of endpoint from specified resources """

    resources = Meta().get_new_classes_from_module(module)

    # Init restful plugin
    if len(resources) > 0:
        rest_api = Api(microservice, catch_all_404s=True)

        # For each RESTful resource i receive
        for resource in resources:

            endpoint, endkey = resource().get_endpoint()
            address = FIXED_APIURL + endpoint
            logger.debug("Adding '%s' resource to REST address: *%s*", \
                resource.__name__, address)

            # Create restful endpoint
            rest_api.add_resource(resource, \
                FIXED_APIURL+endpoint,\
                FIXED_APIURL + endpoint +'/<'+ endkey +'>')

