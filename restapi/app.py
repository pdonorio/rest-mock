#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Flask app creation
"""

from __future__ import division, print_function, absolute_import
from . import myself, lic, get_logger

from flask import got_request_exception, jsonify
from .server import create_app
from .jsonify import log_exception, RESTError

__author__ = myself
__copyright__ = myself
__license__ = lic

logger = get_logger(__name__)

#############################
# BE FLASK
microservice = create_app()
# Custom error handling: save to log
got_request_exception.connect(log_exception, microservice)


#############################
# Custom exceptions
@microservice.errorhandler(RESTError)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

#############################
# We are now ready
microservice.logger.info("*** Our REST API server/app is ready ***")
