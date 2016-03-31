# -*- coding: utf-8 -*-

"""
Decorating my REST API resources.

Decorate is a cool but dangerous place in Python i guess.
Here i am testing different kind of decorations for different problems.

YET TO TEST: from functools import wraps

Restful resources are Flask Views classes. Docs talks about their decoration:
http://flask-restful.readthedocs.org/en/latest/extending.html#resource-method-decorators
So... you should also read better this section of Flask itself:
http://flask.pocoo.org/docs/0.10/views/#decorating-views

I didn't manage to have it play the way docs require, so i tested some slightly
different solutions.
"""

from __future__ import division, absolute_import
from .. import myself, lic, get_logger

from flask.ext.restful import marshal
from flask.wrappers import Response
from .. import htmlcodes as hcodes
from ..meta import Meta

__author__ = myself
__copyright__ = myself
__license__ = lic

logger = get_logger(__name__)


#################################
# Adding an identifier to a REST class
# https://andrefsp.wordpress.com/2012/08/23/writing-a-class-decorator-in-python

def enable_endpoint_identifier(name='myid', idtype='string'):
    """
    Class decorator for ExtendedApiResource objects;
    Enable identifier and let you choose name and type.
    """
    def class_rebuilder(cls):   # decorator

        def init(self):
            logger.info("[%s] Applying ID to endopoint:%s of type '%s'"
                        % (self.__class__.__name__, name, idtype))
            self.set_method_id(name, idtype)
            # logger.debug("New init %s %s" % (name, idtype))
            super(cls, self).__init__()

        NewClass = Meta.metaclassing(
            cls, cls.__name__ + '_withid', {'__init__': init})
        return NewClass
    return class_rebuilder


#################################
# Adding a parameter to method
# ...this decorator took me quite a lot of time...

# In fact, it is a decorator which requires special points:
# 1. chaining: more than one decorator of the same type stacked
# 2. arguments: the decorator takes parameters
# 3. works for a method of class: not a single function, but with 'self'

# http://scottlobdell.me/2015/04/decorators-arguments-python/

def add_endpoint_parameter(name, ptype=str, default=None, required=False):
    """ 
    Add a new parameter to the whole endpoint class.
    Parameters are the ones passed encoded in the url, e.g.

    GET /api/myendpoint?param1=string&param2=42

    Note: it could become specific to the method with using subarrays
    Another note: you could/should use JSON instead...
    """
    def decorator(func):
        def wrapper(self, *args, **kwargs):
            # Debug
            class_name = self.__class__.__name__
            logger.debug("[Class: %s] Decorated to add parameter '%s'"
                         % (class_name, name))

            params = {
                'name': name,
                # Check list type? for filters
                'mytype': ptype,
                'default': default,
                'required': required,
            }
            self.add_parameter(**params)
            return func(self, *args, **kwargs)
        return wrapper
    return decorator


##############################
# Defining a generic decorator for restful methods

# It will assure to have all necessary things up:

# 1. standard json data returns
# N.B. may change it: read here to be sure
# http://mattupstate.com/python/2013/06/26/
#   how-i-structure-my-flask-applications.html#s2g

# 2. also to have my requested parameters configured and parsed
# right before the function call
# this is necessary for the plugin Restful
# http://flask-restful.readthedocs.org/en/latest/reqparse.html
# N.B. will change it for marshmallow?
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
        logger.info("[Class: %s] %s request" % (class_name, method_name))

        # Call the parse method
        self.apply_parameters()
        self.parse()
        # Call the wrapped function
        try:
            out = func(self, *args, **kwargs)
        except KeyError as e:
            error = str(e).strip("'")
            if error == "security":
                return {'message': "FAIL: problems with auth check"}, \
                    hcodes.HTTP_BAD_NOTFOUND
            raise e
        except TypeError as e:
            logger.warning(e)
            error = str(e).strip("'")
            if "required positional argument" in error:
                return {'message': "FAIL: missing argument"}, \
                    hcodes.HTTP_BAD_REQUEST
            raise e

        # DO NOT INTERCEPT 404 or status from other plugins (e.g. security)
        if isinstance(out, Response):
            return out

        # BASE STATUS?
        status = hcodes.HTTP_OK_BASIC

        # VERY IMPORTANT
        # DO NOT INTERFERE when
        # at some level we already provided the couple out/response
        if isinstance(out, tuple) and len(out) == 2:
            subout, status = out
            out = subout

        # Set standards for my response as specified in base.py
        #return marshal(out, self.resource_fields), status
        return out, status

    return wrapper


##############################
# A decorator for the whole class

def all_rest_methods(decorator):
    """ Decorate all the api methods inside one class """

# ADD OTHER METHODS HERE, IF SOME ARE MISSING
    api_methods = ['get', 'post', 'put', 'patch', 'delete']  # , 'search']

    def decorate(cls):
        # there's propably a better way to do this
        for attr in cls.__dict__:
            # Check if method and in it's in my list
            if attr in api_methods and callable(getattr(cls, attr)):
                logger.debug("Decorating %s as api method"
                             % (cls.__name__ + "." + attr))
                setattr(cls, attr, decorator(getattr(cls, attr)))
        return cls
    return decorate
