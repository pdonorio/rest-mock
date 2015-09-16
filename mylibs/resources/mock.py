#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Mock Resource """

from mylibs.resources.base import ExtendedApiResource, returnstandarddata

class Foo(ExtendedApiResource):
    """ Empty example for mock service """

    @returnstandarddata
    def get(self):
        return {'hello': 'world'}
