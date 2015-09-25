#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Main server code logic for this project
"""

from mylibs import get_logger
logger = get_logger(__name__)

####################################
# Create app
from flask import Flask
microservice = Flask(__name__)
# and then add every other needed part

####################################
# Allow cross-domain requests
# e.g. for JS and Upload
from flask_cors import CORS
CORS(microservice, headers=['Content-Type'])
# cors write too much, let's fix it
import logging
corslogger = logging.getLogger('mylibs.server.cors')
corslogger.setLevel(logging.WARNING)

####################################
# RESTful stuff

from flask_restful import Api
rest_api = Api(microservice, catch_all_404s=True)
# automatic Resources
from mylibs.resources.endpoints import Endpoints
epo = Endpoints(rest_api)
# Verify configuration
from mylibs.config import MyConfigs
resources = MyConfigs().rest()

# Basic: from a module mock
if len(resources) < 1:
    logger.info("No file configuration found (or no section inside)")
    from mylibs.resources import exampleservices as mymodule
    epo.many_from_module(mymodule)
# Advanced: from a module mock
else:
    logger.info("Using resources found in configuration")

    for myclass, instance, endpoint, endkey in resources:
        # Load each resource
        epo.create_single(myclass, endpoint, endkey)

####################################
# The End?
