#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Main server factory
"""

import logging
from flask import Flask
from flask_cors import CORS
from flask_restful import Api
from mylibs import get_logger
logger = get_logger(__name__)

####################################
# Create app
microservice = Flask(__name__)
logger.debug("Created application")
# and then add every other needed part

####################################
# Allow cross-domain requests
# e.g. for JS and Upload
CORS(microservice, headers=['Content-Type'])
# cors write too much, let's fix it
corslogger = logging.getLogger('mylibs.server.cors')
corslogger.setLevel(logging.WARNING)

####################################
# RESTful stuff

#from mylibs.resources.base import errors
rest_api = Api(microservice, catch_all_404s=True) #, errors=errors)
