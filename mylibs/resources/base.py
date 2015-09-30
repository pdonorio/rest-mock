#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Basic Resource """

from mylibs import get_logger
logger = get_logger(__name__)

##############################
# Json Serialization as written in restful docs
import simplejson as json
from flask import make_response
def output_json(data, code, headers=None):
    """Makes a Flask response with a JSON encoded body"""
    resp = make_response(json.dumps(data), code)
    resp.headers.extend(headers or {})
    return resp

##############################
# Extending the concept of rest generic resource
from flask_restful import Resource, abort, reqparse, fields
import mylibs.htmlcodes as hcodes

class ExtendedApiResource(Resource):
    """
    Implement a generic Resource for Restful model.

    Note: PUT method differs from POST because data_key is mandatory.
    """

    myname = __name__
    _args = {}
    _params = {}
    endpoint = None
    endtype = 'string:myid'

    ###################################
    hcode = hcodes.HTTP_OK_BASIC
    resource_fields = {
        'status': fields.Integer,
        'response': fields.Raw
        #'response': fields.String(default='Empty message'),
    }

    def response(self, obj=None, fail=False):
        status = hcodes.HTTP_OK_BASIC
        if fail:
            status = hcodes.HTTP_BAD_REQUEST
            abort(status, error=obj)

# // TO FIX:
# How to avoid in abort case?
# Could i add my own encoder for data?

        return {
            'status': status,
            # Json serialization
            #'response': json.dumps(obj)
            'response': obj,
        }
    ###################################

    def __init__(self):
        super(ExtendedApiResource, self).__init__()
        # Be sure of using JSON
        self.representations = {
            'application/json': output_json,
        }
        # Apply decision about the url of endpoint
        self.set_endpoint()
        # Make sure you can parse arguments at every call
        self._parser = reqparse.RequestParser()

    @staticmethod
    def clean_parameter(param=""):
        """ I get parameters already with '"' quotes from curl? """
        if param == None:
            return param
        return param.strip('"')

    def parse(self):
        """ Parameters may be necessary at any method """
        self._args = self._parser.parse_args()

    def set_endpoint(self):
        if self.endpoint is None:
            self.endpoint = type(self).__name__.lower().replace("resource", "")

    def get_endpoint(self):
        return (self.endpoint, self.endtype)

    def add_parameter(self, name, mytype):
        """ Save a parameter inside the class """
        self._params[name] = mytype

    def apply_parameters(self):
        """ Use parameters received via decoration """

        ##############################
        # Basic options
        basevalue = str #Python3
        #basevalue = unicode #Python2
        act = 'store' #store is normal, append is a list
        loc = ['headers', 'values'] #multiple locations
        trim = True

        # # Extra parameter id for POST updates or key forcing
        # self.parser.add_argument("myid", type=basevalue)

        for param, param_type in self._params.items():
            # Decide what is left for this parameter
            if param_type is None:
                param_type = basevalue
# // TO FIX:
# let the user specify if it's required
            required = False
            default = None

            # I am creating an option to handle arrays:
            if param_type == 'makearray':
                param_type = basevalue
                act = 'append'
            self._parser.add_argument(param, type=param_type, \
                default=default, required=required, trim=trim, \
                action=act, location=loc)
            logger.debug("Accept param '%s', type %s" % (param, param_type))

    def remove_id(self):
        """ Avoid the chance to have api/method/:id """
        self.endtype = None
