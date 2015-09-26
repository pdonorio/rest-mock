#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Mock Resources as Example """

from mylibs import get_logger
logger = get_logger(__name__)

from mylibs.resources.base \
    import ExtendedApiResource, standardata, for_all_api_methods

@for_all_api_methods(standardata)
class Foo(ExtendedApiResource):
    """ Empty example for mock service """

    def get(self):
        return {'hello': 'world'}

@for_all_api_methods(standardata)
class FooFoo(ExtendedApiResource):
    """ Empty example with different endpoint """
    endpoint = 'another/path'

    def get(self, myid=None):
        logger.debug("Using different endpoint")
        if myid is not None:
            logger.info("Using data key '%s'" % myid)
            return self.fail("error")
        return {'hello': 'new endpoint'}

    def post(self):
        pass
