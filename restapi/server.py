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

__author__ = myself
__copyright__ = myself
__license__ = lic

logger = get_logger(__name__)


def create_app(name=__name__, **kwargs):
    """ Create the istance for Flask application """

    #################################################
    # Flask app instance
    #################################################
    from confs import config
    microservice = Flask(name,
                         # Quick note:
                         # i use the template folder from the current dir
                         # just for Administration.
                         # I expect to have 'admin' dir here to change
                         # the default look of flask-admin
                         template_folder=config.BASE_DIR,
                         **kwargs)
    # Handling exceptions with json
    for code in default_exceptions.keys():
        microservice.error_handler_spec[None][code] = make_json_error

    ##############################
    # Flask configuration from config file
# TO FIX: development/production split?
    microservice.config.from_object(config)
    logger.info("FLASKING! Created application")

    #################################################
    # Other components
    #################################################

    ##############################
    # Cors
    from .cors import cors
    cors.init_app(microservice)
    logger.info("FLASKING! Injected CORS")

    ##############################
    # DB
    from .models import db, User, Role
    db.init_app(microservice)
    logger.info("FLASKING! Injected sqlalchemy")

    ##############################
    # Flask security
    from flask.ext.security import Security, SQLAlchemyUserDatastore
    udstore = SQLAlchemyUserDatastore(db, User, Role)
    security = Security(microservice, udstore)

    # Prepare database and tables
    with microservice.app_context():
        try:
            if config.REMOVE_DATA_AT_INIT_TIME:
                db.drop_all()
            db.create_all()
            if not User.query.first():
                udstore.create_role(name=config.ROLE_ADMIN, description='King')
                udstore.create_role(name=config.ROLE_USER, description='User')
                from flask_security.utils import encrypt_password
                udstore.create_user(first_name='User', last_name='IAm',
                                    email=config.USER,
                                    password=encrypt_password(config.PWD))
                udstore.add_role_to_user(config.USER, config.ROLE_ADMIN)
                db.session.commit()
                logger.info("Database initizialized with user/roles from conf")
            logger.info("DB: Connected and ready")
        except Exception as e:
            logger.critical("Database connection failure: %s" % str(e))
            exit(1)

    ##############################
    # Restful plugin
    from .rest import rest
    rest.init_app(microservice)
    logger.info("FLASKING! Injected rest endpoints")
    logger.info("FLASKING! Injected security")

    ##############################
    # Flask admin

    # # Define a context processor for merging flask-admin's template context
    # # into the flask-security views
    # @security.context_processor
    # def security_context_processor():
    #     return dict(admin_base_template=admin.base_template,
    #                 admin_view=admin.index_view, h=admin_helpers)

    ##############################
    # App is ready
    return microservice
