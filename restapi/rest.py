#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
App specifications
"""

from __future__ import division, print_function, absolute_import
from . import myself, lic, get_logger

from flask_restful import Api
from .config import MyConfigs
from .resources.endpoints import Endpoints

__author__ = myself
__copyright__ = myself
__license__ = lic

logger = get_logger(__name__)

####################################
# RESTful stuff activation
errors = {}  # for defining future custom errors
rest = Api(catch_all_404s=True, errors=errors)
logger.debug("Flask: creating REST")

# Defining AUTOMATIC Resources
epo = Endpoints(rest)
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
