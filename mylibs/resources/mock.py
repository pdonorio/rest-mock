#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Mock Resource """

import logging
logger = logging.getLogger(__name__)
from mylibs.resources.base import ExtendedApiResource, returnstandarddata

class Foo(ExtendedApiResource):
    """ Empty example for mock service """

    @returnstandarddata
    def get(self):
        logger.debug("Get request")
        return {'hello': 'world'}
