#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Mock Resource """

from mylibs.resources.base import ExtendedApiResource

class Foo(ExtendedApiResource):
    def get(self):
        return {'hello': 'world'}

