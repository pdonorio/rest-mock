#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Basic Resource """

from mylibs import get_logger
logger = get_logger(__name__)

##############################
import simplejson as json

def standardata(func):
    """ 
    Decorate methods to return the most standard json data
    and also to parse available args before using them in the function
    """
    def wrapper(self, *args, **kwargs):
        self.parse()
        data = func(self, *args, **kwargs)
        jdata = json.dumps(data)    #, default=ownc_encoder)
        return jdata
    return wrapper

##############################
# Rest generic resource
from flask_restful import Resource, abort, reqparse
import mylibs.htmlcodes as hcodes

class ExtendedApiResource(Resource):
    """
    Implement a generic Resource for Restful model.

    Note: PUT method differs from POST because data_key is mandatory.
    """

    myname = __name__
    endpoint = None
    endtype = 'string:myid'

    def __init__(self):
        super(ExtendedApiResource, self).__init__()
        self.set_endpoint()
        self._parser = reqparse.RequestParser()
        self._args = None

    @staticmethod
    def clean_parameter(param=""):
        """ I get parameters already with '"' quotes from curl? """
        if param == None:
            return param
        return param.strip('"')

    def parse(self):
        """ Parameters may be necessary at any method """
        self._args = self._parser.parse_args()

    def fail(self, message="geeric error"):
        return abort(hcodes.HTTP_BAD_REQUEST, message=message)

    def set_endpoint(self):
        if self.endpoint is None:
            self.endpoint = type(self).__name__.lower().replace("resource", "")

    def get_endpoint(self):
        return (self.endpoint, self.endtype)
