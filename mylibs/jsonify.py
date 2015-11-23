#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Specialized JSON-oriented Flask App.

Why?
When things go wrong, default errors that Flask/Werkzeug respond are all HTML.
Which breaks the clients who expect JSON back even in case of errors.

source: http://flask.pocoo.org/snippets/83/
"""

import simplejson as json
from flask import Flask, jsonify, make_response
from werkzeug.exceptions import default_exceptions
from werkzeug.exceptions import HTTPException
from . import htmlcodes as hcodes

__all__ = ['make_json_app']


##############################
# Json Serialization for more than simple returns

# // TO FIX:
# Could this be moved/improved?
# see http://flask.pocoo.org/snippets/20/

def make_json_app(import_name, **kwargs):
    """ Creates a JSON-oriented Flask app. """
    def make_json_error(ex):
        response = jsonify(message=str(ex))
        response.status_code = (ex.code if isinstance(ex, HTTPException)
                                else hcodes.HTTP_DEFAULT_SERVICE_FAIL)
        return response

    app = Flask(import_name, **kwargs)

    for code in default_exceptions.keys():
        app.error_handler_spec[None][code] = make_json_error

    return app


##############################
# Json Serialization as written in restful docs
def output_json(data, code, headers=None):
    """Makes a Flask response with a JSON encoded body"""
    resp = make_response(json.dumps(data), code)
    resp.headers.extend(headers or {})
    return resp


####################################
# Custom error handling: SAVE TO LOG
# http://flask-restful.readthedocs.org/en/latest/
# extending.html#custom-error-handlers
def log_exception(sender, exception, **extra):
    """ Log an exception to our logging framework """
    sender.logger.error('Got exception during processing: %s', exception)


##############################
# My rest exception class, extending Flask
# http://flask.pocoo.org/docs/0.10/patterns/apierrors/#simple-exception-class
class RESTError(Exception):

    status_code = hcodes.HTTP_BAD_REQUEST

    def __init__(self, message, status_code=None, payload=None):
        # My exception
        Exception.__init__(self)
        # Variables
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv
