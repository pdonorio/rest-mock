#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Decorating my resources.

Restful resources are Flask Views classes. Docs talks about their decoration:
http://flask-restful.readthedocs.org/en/latest/extending.html#resource-method-decorators
So... you should also read better this section of Flask itself:
http://flask.pocoo.org/docs/0.10/views/#decorating-views

I didn't manage to have it play the way docs require, so i tested some slightly
different solutions.
YET TO TEST: from functools import wraps

Also
Restful suggests to use "with marshal" for nested outputs:
http://flask-restful.readthedocs.org/en/latest/fields.html#advanced-nested-field


"""

from mylibs import get_logger
logger = get_logger(__name__)

from flask_restful import marshal_with, marshal

#################################
# This decorator took me quite a lot of time

# In fact, it is a decorator which requires special points:
# 1. chaining: more than one decorator of the same type stacked
# 2. arguments: the decorator takes parameters
# 3. works for a method of class: not a single function, but with 'self'

# http://scottlobdell.me/2015/04/decorators-arguments-python/

class add_endpoint_parameter(object):
    """ A class as DECORATOR seems to fit the most strange situations """

    def __init__(self, name, ptype=str):
        self.name = name
        self.ptype = ptype

    def __call__(self, fn, *args, **kwargs):

        params = {
            'name': self.name,
            'mytype': self.ptype,
        }
        def new_func(self, *args, **kwargs):
            self.add_parameter(**params)
            return fn(self, *args, **kwargs)
        return new_func

##############################
# Defining a generic decorator for restful methods

# It will assure to have all necessary things up:

# 1. standard json data returns
# N.B. may change it: read here to be sure
#http://mattupstate.com/python/2013/06/26/how-i-structure-my-flask-applications.html#s2g

# 2. also to have my requested parameters configured and parsed
# right before the function call
# this is necessary for the plugin Restful
# http://flask-restful.readthedocs.org/en/latest/reqparse.html
# N.B. will change it for marshmallow?
# http://marshmallow.readthedocs.org/en/latest/

def apimethod(func):
    """ 
    Decorate methods to return the most standard json data
    and also to parse available args before using them in the function
    """
    def wrapper(self, *args, **kwargs):
        # Debug
        class_name = self.__class__.__name__
        method_name = func.__name__.upper()
        logger.info("[Class: %s] %s request" % \
            (class_name, method_name) )

        # Call the parse method
        self.apply_parameters()
        self.parse()

        # Call the wrapped function
        out = func(self, *args, **kwargs)

        # Set standards for my response as specified in base.py
        return marshal(out, self.resource_fields)
    return wrapper

##############################
# Since my previous decorator would be necessary
# for any typical method inside a rest resource
# such as GET, POST, PUT, DELETE (and more?)
# i looked for a solution online
# Source:
# http://stackoverflow.com/a/6307868/2114395

def all_rest_methods(decorator):
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
