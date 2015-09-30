#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Basic Resource """

from mylibs import get_logger
logger = get_logger(__name__)

##############################
# Extending the concept of rest generic resource
from flask_restful import Resource, abort, reqparse
import mylibs.htmlcodes as hcodes

class ExtendedApiResource(Resource):
    """
    Implement a generic Resource for Restful model.

    Note: PUT method differs from POST because data_key is mandatory.
    """

    myname = __name__
    _params = {}
    endpoint = None
    endtype = 'string:myid'
    _args = {}

    def __init__(self):
        super(ExtendedApiResource, self).__init__()
        self.set_endpoint()
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

    def accepted(self, key=None):
        if key is None:
            key = 1
# // TO FIX:
# non standard...
        return key, hcodes.HTTP_OK_CREATED

    def fail(self, message="geeric error"):
        return abort(hcodes.HTTP_BAD_REQUEST, message=message)

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
