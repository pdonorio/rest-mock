#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Basic Resource """

from mylibs import get_logger
logger = get_logger(__name__)

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
def all_api_methods(decorator):
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
