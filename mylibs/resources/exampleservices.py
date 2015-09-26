#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Mock Resources as Example """

from mylibs import get_logger
logger = get_logger(__name__)

from mylibs.resources.base \
    import ExtendedApiResource, standardata, for_all_api_methods

#####################################
## FIRST simple EXAMPLE

# Reply to:
# GET /api/foo

@for_all_api_methods(standardata)
class Foo(ExtendedApiResource):
    """ Empty example for mock service with no :id """

    def __init__(self):
        super(Foo, self).__init__()
        # Make sure to avoid resource /api/foo/:id
        self.remove_id()

    def get(self):
        return {'hello': 'world'}

#####################################
## SECOND and more complex EXAMPLE

# Reply to:
# GET /api/another/path
# GET /api/another/path/:id
# POST /api/another/path (with null)

@for_all_api_methods(standardata)
class FooFoo(ExtendedApiResource):
    """ Empty example with different endpoint """
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
