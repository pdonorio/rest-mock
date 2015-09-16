#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Basic Resource """

##############################
import simplejson as json

def returnstandarddata(func):
    """ Decorate to standard return json data """
    def wrapper(*args):
        data = func(*args)
        jdata = json.dumps(data)    #, default=ownc_encoder)
        return jdata
    return wrapper

##############################
# Rest generic resource
from flask_restful import Resource

class ExtendedApiResource(Resource):
    """ Implement a generic Resource for Restful model """

    myname = __name__
    endpoint = None
    endtype = 'string:data_key'

    def __init__(self):
        super(ExtendedApiResource, self).__init__()
        self.set_endpoint()

    @staticmethod
    def clean_parameter(param=""):
        """ I get parameters already with '"' quotes from curl? """
        if param == None:
            return param
        return param.strip('"')

    def set_endpoint(self):
        if self.endpoint is None:
            self.endpoint = type(self).__name__.lower().replace("resource", "")

    def get_endpoint(self):
        return (self.endpoint, self.endtype)
