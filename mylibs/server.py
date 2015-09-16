#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Flask hello world """

import logging
logger = logging.getLogger(__name__)

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

####################################
# RESTful
from flask_restful import Api
rest_api = Api(microservice, catch_all_404s=True)
# automatic Resources
from mylibs import RES_CONFIG
from mylibs.resources import create_endpoint, create_endpoints

##########################
# From configuration
import configparser
# Make sure configuration is case sensitive
config = configparser.RawConfigParser()
config.optionxform = str
# read ?
config.read(RES_CONFIG)
sections = config.sections()

# Do modules
if len(sections) > 0:

    from importlib import import_module
    logger.info("Using configuration from " + RES_CONFIG)

    for section in sections:
        logger.debug("Section " + section)

        # Meta language for dinamically import
        try:
            module = import_module('mylibs.resources.' + section)
        except ImportError as e:
            logger.critical("Failed to load resource: " + str(e))
            continue

        for classname, endpoint in config[section].items():
            # Meta language for dinamically import
            try:
                myclass = getattr(module, classname)
                logger.info("Found " + section + '.' + classname)
            except AttributeError as e:
                logger.critical("Failed to load resource: " + str(e))
                continue

            instance = myclass()
            oldendpoint, endkey = instance.get_endpoint()
            if endpoint.strip() == '':
                endpoint = oldendpoint

            # Load
            create_endpoint(rest_api, myclass, endpoint, endkey)

##########################
# Basic: from a module mock
else:
    logger.info("Using default mock")
    from mylibs.resources import mock as mymodule
    create_endpoints(rest_api, mymodule)
