#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Main server factory.
We create all the components here!
"""

from __future__ import division, print_function, absolute_import
from . import myself, lic, get_logger

import os
from flask import Flask, got_request_exception, jsonify
from .jsonify import make_json_error
from werkzeug.exceptions import default_exceptions
from .jsonify import log_exception, RESTError

__author__ = myself
__copyright__ = myself
__license__ = lic

logger = get_logger(__name__)


def create_app(name=__name__, security=True, **kwargs):
    """ Create the istance for Flask application """

    #################################################
    # Flask app instance
    #################################################
    from confs import config
    template_dir = os.path.join(config.BASE_DIR, __package__)
    microservice = Flask(name,
                         # Quick note:
                         # i use the template folder from the current dir
                         # just for Administration.
                         # I expect to have 'admin' dir here to change
                         # the default look of flask-admin
                         template_folder=template_dir,
                         **kwargs)

    ##############################
    # ERROR HANDLING

    # Handling exceptions with json
    for code in default_exceptions.keys():
        microservice.error_handler_spec[None][code] = make_json_error
    # Custom error handling: save to log
    got_request_exception.connect(log_exception, microservice)

    # Custom exceptions
    @microservice.errorhandler(RESTError)
    def handle_invalid_usage(error):
        response = jsonify(error.to_dict())
        response.status_code = error.status_code
        return response

    ##############################
    # Flask configuration from config file

# // TO FIX:
# development/production split?

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

    if security:
        ##############################
        # DB
        from .models import db, User, Role
        db.init_app(microservice)
        logger.info("FLASKING! Injected sqlalchemy")

        ##############################
        # Flask security
        from flask.ext.security import Security, SQLAlchemyUserDatastore
        udstore = SQLAlchemyUserDatastore(db, User, Role)
        auth = Security(microservice, udstore)
        logger.info("FLASKING! Injected security")

        # Prepare database and tables
        with microservice.app_context():
            try:
                if config.REMOVE_DATA_AT_INIT_TIME:
                    db.drop_all()
                db.create_all()
                if not User.query.first():
                    udstore.create_role(name=config.ROLE_ADMIN,
                                        description='King')
                    udstore.create_role(name=config.ROLE_USER,
                                        description='User')
                    from flask_security.utils import encrypt_password
                    udstore.create_user(first_name='User', last_name='IAm',
                                        email=config.USER,
                                        password=encrypt_password(config.PWD))
                    udstore.add_role_to_user(config.USER, config.ROLE_ADMIN)
                    db.session.commit()
                    logger.info("Database init with user/roles from conf")
                logger.info("DB: Connected and ready")
            except Exception as e:
                logger.critical("Database connection failure: %s" % str(e))
                exit(1)

    ##############################
    # Restful plugin
    from .rest import rest
    rest.init_app(microservice)
    logger.info("FLASKING! Injected rest endpoints")

    ##############################
    # Flask admin
    if security:
        from .admin import admin, UserView, RoleView
        from flask_admin import helpers as admin_helpers
        admin.init_app(microservice)
        admin.add_view(UserView(User, db.session))
        admin.add_view(RoleView(Role, db.session))

        # Define a context processor for merging flask-admin's template context
        # into the flask-security views
        @auth.context_processor
        def security_context_processor():
            return dict(admin_base_template=admin.base_template,
                        admin_view=admin.index_view, h=admin_helpers)

    ##############################
    # App is ready
    return microservice
