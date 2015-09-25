#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Mock Resources as Example """

from mylibs import get_logger
logger = get_logger(__name__)

from mylibs.resources.base import ExtendedApiResource, standardata

class Foo(ExtendedApiResource):
    """ Empty example for mock service """

    @standardata
    def get(self):
        logger.debug("Get request")
        return {'hello': 'world'}

class FooFoo(ExtendedApiResource):
    """ Empty example with different endpoint """

    endpoint = 'another/path'

    @standardata
    def get(self, myid=None):
        logger.debug("Using different endpoint")
        if myid is not None:
            logger.info("Using data key '%s'" % myid)
            return self.fail("error")
        return {'hello': 'new endpoint'}
