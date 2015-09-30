#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
App specifications
"""

from mylibs.server import microservice, rest_api
from mylibs.resources.endpoints import Endpoints
from mylibs.config import MyConfigs

from mylibs import get_logger
logger = get_logger(__name__)

######################################################
# from flask import Response
# from mylibs.resources.base import errors
# for key, error in errors.items():
#     print(error)
#     # http://stackoverflow.com/a/8316995/2114395
#     @microservice.errorhandler(400)
#     def custom_400(error):
#         return Response('<Why access is denied string goes here...>', 400, {'WWWAuthenticate':'Basic realm="Login Required"'})

######################################################
# From my code: defining automatic Resources
epo = Endpoints(rest_api)
# Verify configuration
resources = MyConfigs().rest()

# Basic configuration (simple): from example class
if len(resources) < 1:
    logger.info("No file configuration found (or no section inside)")
    from mylibs.resources import exampleservices as mymodule
    epo.many_from_module(mymodule)
# Advanced configuration (cleaner): from your module and .ini
else:
    logger.info("Using resources found in configuration")

    for myclass, instance, endpoint, endkey in resources:
        # Load each resource
        epo.create_single(myclass, endpoint, endkey)

####################################
# Take this app from main
microservice.logger.info("*** Our REST API server app is ready ***")
