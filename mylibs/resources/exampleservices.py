#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Mock Resources as Example """

import logging
logger = logging.getLogger(__name__)

from mylibs.resources.base import ExtendedApiResource, returnstandarddata

class Foo(ExtendedApiResource):
    """ Empty example for mock service """

    @returnstandarddata
    def get(self):
        logger.debug("Get request")
        return {'hello': 'world'}

class FooFoo(ExtendedApiResource):
    """ Empty example with different endpoint """

    endpoint = 'another/path'

    @returnstandarddata
    def get(self):
        logger.debug("Using different endpoint")
        return {'hello': 'new endpoint'}
