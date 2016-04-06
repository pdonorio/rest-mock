# -*- coding: utf-8 -*-

"""
Test  dataobjects endpoints
"""

# import os
# import sys
from restapi.server import create_app

# from nose.tools import assert_equals
# from nose.tools import with_setup

__author__ = 'Roberto Mucci (r.mucci@cineca.it)'


class TestDataObjects(object):

    @classmethod
    def setup_class(cls):
        "set up test fixtures"
        print('*******************ciao')
        cls.app = create_app().test_client()
        cls.app.config['TESTING'] = True

    @classmethod
    def teardown_class(cls):
        "tear down test fixtures"

    #@with_setup(setup_func, teardown_func)
    def test_get_dataobjects(self):
        """ GET dataobjects """
        r = self.app.get('http://localhost:8080/api/verify')
        print (r.text)
