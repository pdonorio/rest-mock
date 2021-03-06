# -*- coding: utf-8 -*-

"""
App specifications
"""

from __future__ import division, absolute_import
from . import myself, lic, get_logger

from flask_restful import Api, Resource
from .resources.endpoints import Endpoints
from .config import MyConfigs

__author__ = myself
__copyright__ = myself
__license__ = lic

logger = get_logger(__name__)

####################################
# REST activation

errors = {}  # for defining future custom errors
# Restful plugin
rest = Api(catch_all_404s=True, errors=errors)
# Defining AUTOMATIC Resources
epo = Endpoints(rest)
logger.debug("Flask: creating REST")


def create_endpoints(custom_epo, security=False, debug=False):
    """ A single method to add all endpoints """

    ####################################
    # HELLO WORLD endpoint...
    @rest.resource('/', '/hello')
    class Hello(Resource):
        """ Example with no authentication """
        def get(self):
            return "Hello world", 200
    logger.debug("Base endpoint: Hello world!")

    ####################################
    # Verify configuration
    resources = MyConfigs().rest()

    ####################################
    # Basic configuration (simple): from example class
    if len(resources) < 1:
        logger.info("No file configuration found (or no section inside)")
        from .resources import exampleservices as mymodule
        custom_epo.many_from_module(mymodule)
    # Advanced configuration (cleaner): from your module and .ini
    else:
        logger.info("Using resources found in configuration")

        for myclass, instance, endpoint, endkey in resources:
            # Load each resource
            custom_epo.create_single(myclass, endpoint, endkey)

    ####################################
    # Verify functions on the API server
    if security:
        from .resources import checkauth
        custom_epo.many_from_module(checkauth)
    else:
        from .resources.checkauth import Verify
        custom_epo.create_many([Verify])

    ####################################
    # Profile endpoint
    from .resources import profiles
    custom_epo.many_from_module(profiles)

    ####################################
    # The end
    return custom_epo
