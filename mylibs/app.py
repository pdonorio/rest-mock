#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
App specifications
"""

################################
from __future__ import division, print_function, absolute_import
from . import myself, lic, get_logger

from flask import got_request_exception, jsonify
from .server import microservice, rest_api
from .resources.endpoints import Endpoints
from .config import MyConfigs
from .jsonify import log_exception, RESTError

__author__ = myself
__copyright__ = myself
__license__ = lic

logger = get_logger(__name__)

######################################################
# From my code: defining automatic Resources
epo = Endpoints(rest_api)
# Verify configuration
resources = MyConfigs().rest()

# Basic configuration (simple): from example class
if len(resources) < 1:
    logger.info("No file configuration found (or no section inside)")
    from .resources import exampleservices as mymodule
    epo.many_from_module(mymodule)
# Advanced configuration (cleaner): from your module and .ini
else:
    logger.info("Using resources found in configuration")

    for myclass, instance, endpoint, endkey in resources:
        # Load each resource
        epo.create_single(myclass, endpoint, endkey)

####################################
# Custom error handling: save to log
got_request_exception.connect(log_exception, microservice)


####################################
# Custom exception
@microservice.errorhandler(RESTError)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

####################################
# Take this app from main
microservice.logger.info("*** Our REST API server/app is ready ***")
