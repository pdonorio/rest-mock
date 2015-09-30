#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Mock Resources as Example """

# In case you do not know how API endpoints usually looks,
# see some examples here to take inspiration
# https://parse.com/docs/rest/guide

from mylibs import get_logger
logger = get_logger(__name__)

from mylibs.resources.base import ExtendedApiResource
import mylibs.resources.decorators as decorate

#####################################
## FIRST simple EXAMPLE

## Works with requests to:
# GET /api/foo

@decorate.all_rest_methods(decorate.apimethod)
class FooOne(ExtendedApiResource):
    """ Empty example for mock service with no :id """

    def __init__(self):
        super(FooOne, self).__init__()
        # Make sure to avoid resource /api/foo/:id
        self.remove_id()

    def get(self):
        return {'hello': 'world'}

#####################################
## SECOND and more complex EXAMPLE

## Works with requests to:
# GET /api/another/path
# GET /api/another/path/:id
# POST /api/another/path (with null)

@decorate.all_rest_methods(decorate.apimethod)
class FooTwo(ExtendedApiResource):
    """ Example with use of id """

    endpoint = 'another/path'

    def get(self, myid=None):
        logger.debug("Using different endpoint")
        # I want to check if /api/another/path/id is empty
        if myid is not None:
            logger.info("Using data key '%s'" % myid)
            return self.fail("error")
        return {'hello': 'new endpoint'}

    def post(self):
        pass

#####################################
## THIRD EXAMPLE with parameters

## Works with requests to:
# GET /api/another/path?myarg=a
# POST /api/another/path?arg2=3&arg3=test

class FooThree(ExtendedApiResource):
    """
    Example with parameters.

    Add as many parameter in a decorator stack on top of the method.

    BEWARE that to make this work you cannot apply the decorator 'apimethod'
    as before to the whole class with the class decorator. It has to be as
    the most inner decorator of the method itself,
    OTHERWISE NO PARAMETERS WILL BE SEEN.
    """

    # Adding parameter with decorator
    @decorate.add_endpoint_parameter('myarg')
    @decorate.apimethod
    def get(self):
        logger.debug("Received args %s" % self._args)
        return self._args

    # Adding parameters with decorator in different ways
    @decorate.add_endpoint_parameter('arg1', str)
    @decorate.add_endpoint_parameter('arg2', ptype=int)
    @decorate.add_endpoint_parameter(name='arg3', ptype=str)
    @decorate.apimethod
    def post(self):
        logger.debug("Received args %s" % self._args)
        return self.accepted('three [arg3: %s]' % self._args['arg3'])
        #return self.fail()
