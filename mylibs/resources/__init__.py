#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" REST API Resources package """

FIXED_APIURL = '/api' + '/'

from flask_restful import Api

def create_endpoints(resources, microservice):
    """ Automatic creation of endpoint from specified resources """

    rest_api = Api(microservice, catch_all_404s=True)

# // TO FIX: endpoint from the class?
    for resource in resources:
        endpoint, endkey = resource().get_endpoint()

        address = FIXED_APIURL + endpoint
        print("Adding", resource.__name__, "resource to REST address", address)

        # Create restful endpoint
        rest_api.add_resource(resource, \
            FIXED_APIURL+endpoint,\
            FIXED_APIURL + endpoint +'/<'+ endkey +'>')

