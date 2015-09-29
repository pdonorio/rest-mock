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
# POST /api/another/path

#@decorate.all_rest_methods(decorate.apimethod)
class FooThree(ExtendedApiResource):
    """ Example with parameters """

    # Adding parameters with decorator
    @decorate.add_endpoint_parameter(name='test')
    @decorate.add_endpoint_parameter('test2', ptype=int)
    @decorate.apimethod
    def post(self):
        logger.debug("Received args %s" % self._args)
        return self.accepted('three')
        #return self.fail()

"""
Note to self: [YET TO TEST]

You cannot add different parameters inside the same Resource / Class.

In fact you should create a separate resource each time parameters differs
and then bind the two resources into the same endpoint:
"""
