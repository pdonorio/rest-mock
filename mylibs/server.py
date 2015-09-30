#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Main server factory
"""

import logging
from .jsonify import make_json_app
from flask_cors import CORS
from flask_restful import Api
from . import get_logger

logger = get_logger(__name__)

####################################
# Create app - with json responses also in exception
microservice = make_json_app(__name__)
# OLD FASHION:
#from flask import Flask
#microservice = Flask(__name__)
logger.debug("Created application")

# Flask Confs?
# // TO FIX: move it in a file
microservice.config["TRAP_BAD_REQUEST_ERRORS"] = True
microservice.config["PROPAGATE_EXCEPTIONS"] = False

####################################
# Allow cross-domain requests
# e.g. for JS and Upload
CORS(microservice, headers=['Content-Type'])
# cors write too much, let's fix it
corslogger = logging.getLogger('mylibs.server.cors')
corslogger.setLevel(logging.WARNING)

####################################
# RESTful stuff activation
errors = {}
#http://flask-restful.readthedocs.org/en/latest/extending.html#define-custom-error-messages
rest_api = Api(microservice, catch_all_404s=True, errors=errors)
