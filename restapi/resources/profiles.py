# -*- coding: utf-8 -*-

"""
Profiles for internal users
"""

from __future__ import division, absolute_import
from .. import myself, lic, get_logger
from .base import ExtendedApiResource
from . import decorators as deck
from .. import htmlcodes as hcodes

__author__ = myself
__copyright__ = myself
__license__ = lic

logger = get_logger(__name__)


class InitProfile(ExtendedApiResource):
    """ Token authentication test """

    @deck.apimethod
    def post(self):
        j = self.get_input()

        key = 'userid'
        if key not in j:
            return self.response(
                "No user identifier specified to init the profile",
                fail=True, code=hcodes.HTTP_DEFAULT_SERVICE_FAIL)

        return "Yet to do"
