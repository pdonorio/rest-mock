# -*- coding: utf-8 -*-

"""
Main server factory.
We create all the components here!
"""

from __future__ import division, absolute_import
from . import myself, lic, get_logger

import os
from flask import Flask, request, got_request_exception, jsonify
from .jsonify import make_json_error
from werkzeug.exceptions import default_exceptions
from .jsonify import log_exception, RESTError

__author__ = myself
__copyright__ = myself
__license__ = lic

logger = get_logger(__name__)

###############################
# RETHINKDB
RDB_AVAILABLE = False
MODELS = []
if 'RDB_NAME' in os.environ:
    from .resources.services.rethink import load_models, wait_for_connection
    # Look for models
    MODELS = load_models()
    if len(MODELS) > 0:
        RDB_AVAILABLE = True
        wait_for_connection()
        logger.info("Found RethinkDB container")


###############################
def create_app(name=__name__, enable_security=True, debug=False, **kwargs):
    """ Create the server istance for Flask application """

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
        # print("ERROR", error)
        response = jsonify(error.to_dict())
        response.status_code = error.status_code
        return response

    ##############################
    # Flask configuration from config file
    microservice.config.from_object(config)
    microservice.config['DEBUG'] = debug
# // TO FIX:
# development/production split?
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
    from .models import db
    db.init_app(microservice)
    logger.info("FLASKING! Injected sqlalchemy. (please use it)")

    ##############################
    # Flask security
    if enable_security:

        ############################################
# Should open an issue on flask-admin!
        """
        # BUG!
         The following is how it should be, but we get infinite loop:
          File "/usr/local/lib/python3.4/dist-packages/flask_security/core.py"
          , line 450, in __getattr__
            return getattr(self._state, name, None)
        RuntimeError: maximum recursion depth exceeded
        """
        # from .security import security
        # security.init_app(microservice)
# WORKAROUND
        from .security import udstore
        from flask_security import Security
        security = Security(microservice, udstore)
# WORKAROUND
        ############################################

        logger.info("FLASKING! Injected security")

    ##############################
    # Restful plugin
    from .rest import epo, create_endpoints
    logger.info("FLASKING! Injected rest endpoints")
    epo = create_endpoints(epo, security, debug)

    # Restful init of the app
    epo.rest_api.init_app(microservice)

    ##############################
    # Prepare database and tables
    with microservice.app_context():
        try:
            if config.REMOVE_DATA_AT_INIT_TIME:
                db.drop_all()
            db.create_all()
            logger.info("DB: Connected and ready")
        except Exception as e:
            logger.critical("Database connection failure: %s" % str(e))
            exit(1)

        if enable_security:
            from .security import db_auth
            # Prepare user/roles
            db_auth()

    ##############################
    # Flask admin
    if enable_security:
        from .admin import admin, UserView, RoleView
        from .models import User, Role
        from flask_admin import helpers as admin_helpers

        admin.init_app(microservice)
        admin.add_view(UserView(User, db.session))
        admin.add_view(RoleView(Role, db.session))

        # Context processor for merging flask-admin's template context
        # into the flask-security views
        @security.context_processor
        def security_context_processor():
            return dict(admin_base_template=admin.base_template,
                        admin_view=admin.index_view, h=admin_helpers)

        logger.info("FLASKING! Injected admin endpoints")

    ##############################
    # RETHINKDB
# // TO FIX, not for every endpoint
    if RDB_AVAILABLE:
        @microservice.before_request
        def before_request():
            logger.debug("Hello request RDB")
# === Connection ===
# The RethinkDB server doesn’t use a thread-per-connnection approach,
# so opening connections per request will not slow down your database.

# Database should be already connected in "before_first_request"
# But the post method fails to find the object!
            from .resources.services.rethink import try_to_connect
            try_to_connect()

    ##############################
    # Logging responses
    @microservice.after_request
    def log_response(response):
        logger.info("{} {} {}\n{}".format(
                    request.method, request.url, request.data, response))
        return response
    # OR
    # http://www.wiredmonk.me/error-handling-and-logging-in-flask-restful.html
    # WRITE TO FILE
    # file_handler = logging.FileHandler('app.log')
    # app.logger.addHandler(file_handler)
    # app.logger.setLevel(logging.INFO)

    ##############################
    # App is ready
    return microservice
