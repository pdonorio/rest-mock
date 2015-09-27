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

    def __init__(self):
        super(ExtendedApiResource, self).__init__()
        self.set_endpoint()
        self._parser = reqparse.RequestParser()
        self.set_parameters()

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

    def set_parameters(self):

        ##############################
        # Basic options
        basevalue = str #Python3
        #basevalue = unicode #Python2
        act = 'store' #store is normal, append is a list
        loc = ['headers', 'values'] #multiple locations
        trim = True

        # # Extra parameter id for POST updates or key forcing
        # self.parser.add_argument("myid", type=basevalue)

        for (method, params) in self._params.items():
            print(basevalue)
            for param, param_type in params.items():

# // TO FIX:
# no param type selection at the moment
                param_type = basevalue
                required = False
                default = ''

                # I am creating an option to handle arrays:
                if param_type == 'makearray':
                    param_type = basevalue
                    act = 'append'
                self._parser.add_argument(param, type=param_type, \
                    default=default, required=required, trim=trim, \
                    action=act, location=loc)
                logger.debug("Setting parameters: method %s - '%s' of type %s" \
                    % (method.upper(), param, param_type))

    def remove_id(self):
        """ Avoid the chance to have api/method/:id """
        self.endtype = None

# // TO FIX:
## TO MOVE in a decorator class

##############################
# Defining a decorator for restful methods
# to have all necessary things up with standard returns
import simplejson as json

def standardata(func):
    """ 
    Decorate methods to return the most standard json data
    and also to parse available args before using them in the function
    """
    def wrapper(self, *args, **kwargs):
        class_name = self.__class__.__name__
        method_name = func.__name__.upper()
        logger.debug("[Class: %s] %s request" % \
            (class_name, method_name) )
        # Call the parse method
        self.parse()
        data = func(self, *args, **kwargs)
# // TO FIX:
# How to avoid in abort case?
        jdata = json.dumps(data)    #, default=ownc_encoder)
        return jdata
    return wrapper

# Source:
# http://stackoverflow.com/a/6307868/2114395
def for_all_api_methods(decorator):
    """ Decorate all the api methods inside one class """

    api_methods = ['get', 'post', 'put', 'delete']

    def decorate(cls):
        # there's propably a better way to do this
        for attr in cls.__dict__:
            # Check if method and in it's in my list
            if attr in api_methods and callable(getattr(cls, attr)):
                logger.debug("Decorating %s as api method" \
                    % (cls.__name__ + "." + attr) )
                setattr(cls, attr, decorator(getattr(cls, attr)))
        return cls
    return decorate
