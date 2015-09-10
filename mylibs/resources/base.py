#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Basic Resource """

from flask_restful import Resource

class ExtendedApiResource(Resource):
    """ Implement a generic Resource for Restful model """

    myname = __name__
    endtype = 'string:data_key'

    @staticmethod
    def clean_parameter(param=""):
        """ I get parameters already with '"' quotes from curl? """
        if param == None:
            return param
        return param.strip('"')

    def get_endpoint(self):
        self.myname = type(self).__name__.lower().replace("resource", "")
        return (self.myname, self.endtype)
