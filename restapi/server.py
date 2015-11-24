#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Main server factory.
We create all the components here!
"""

from __future__ import division, print_function, absolute_import
from . import myself, lic, get_logger

from .jsonify import make_json_app
from confs import config
# Handle cors...
from flask_cors import CORS
# REST
from flask_restful import Api
# SQL
from flask.ext.sqlalchemy import SQLAlchemy
# Admin interface
from flask_admin import Admin

__author__ = myself
__copyright__ = myself
__license__ = lic

logger = get_logger(__name__)

####################################
# Create app - with json responses also in exception
# (this is where i create the Flask app: called 'microservice')
microservice = make_json_app(__name__, template_folder=config.BASE_DIR)
logger.debug("Created application")
microservice.config.from_object(config)

####################################
# Allow cross-domain requests
# e.g. for JS and Upload
CORS(microservice, headers=['Content-Type'])
logger.debug("Flask: adding CORS")

# # WARNING: in case 'cors' write too much, you could fix it like this
# import logging
# corslogger = logging.getLogger('.server.cors')
# corslogger.setLevel(logging.WARNING)

####################################
# RESTful stuff activation
errors = {}  # for defining future custom errors
rest_api = Api(microservice, catch_all_404s=True, errors=errors)
logger.debug("Flask: adding REST")

####################################
# Create database connection object
db = SQLAlchemy(microservice)
logger.debug("Flask: adding SQLAlchemy")

####################################
# Admininistration
admin = Admin(microservice, name='mytest', template_mode='bootstrap3')
logger.debug("Flask: adding Admininistration")
