#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Main server factory.
We create all the components here!
"""

from __future__ import division, print_function, absolute_import
from . import myself, lic, get_logger

from flask import Flask
from .jsonify import make_json_error
from werkzeug.exceptions import default_exceptions
# # Admin interface
# from flask_admin import Admin

__author__ = myself
__copyright__ = myself
__license__ = lic

logger = get_logger(__name__)

# ####################################
# # Admininistration
# admin = Admin(microservice, name='mytest', template_mode='bootstrap3')
# logger.debug("Flask: creating Admininistration")


####################################
# Create app - with json responses also in exception
# (this is where i create the Flask app: called 'microservice')
def create_app(name=__name__, **kwargs):
    """ Create the istance for Flask application """

    # Flask app instance
    from confs import config
    microservice = Flask(name,
                         template_folder=config.BASE_DIR, **kwargs)

    microservice.config.from_object(config)
    logger.debug("Created application")

    # Handling exceptions with json
    for code in default_exceptions.keys():
        microservice.error_handler_spec[None][code] = make_json_error

    ##############################
    # Other components

    # DB
    from .models import db
    db.init_app(microservice)
    logger.debug("Injected sqlalchemy")
    # Cors
    from .cors import cors
    cors.init_app(microservice)
    logger.debug("Injected CORS")
    # Restful plugin
    from .rest import rest
    rest.init_app(microservice)
    logger.debug("Injected rest endpoints")

    # App is ready
    return microservice
