# -*- coding: utf-8 -*-

"""
Profiles for internal users
"""

from __future__ import division, absolute_import
from .. import myself, lic, get_logger

from .base import ExtendedApiResource
from ..models import db, User, Role
from . import decorators as deck
from .. import htmlcodes as hcodes
from confs import config

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

        key1 = 'name'
        key2 = 'surname'
        if key1 not in j or key2 not in j:
            return self.response(
                "No profile info: name and/or surname",
                fail=True, code=hcodes.HTTP_DEFAULT_SERVICE_FAIL)

        ######################
        user = User.query.get(int(j[key]))
        if user is None:
            return self.response(
                "Invalid account",
                fail=True, code=hcodes.HTTP_DEFAULT_SERVICE_FAIL)

        user.first_name = j[key1]
        user.last_name = j[key2]

        ######################
        # ACTIVE OR NOT
        # # Not active after registration
        user.active = False
        # email confirmation
        user.confirmed_at = None

        # ## To activate:
        # import datetime
        # user.confirmed_at = datetime.datetime.utcnow()

        ######################
        # Base role
        role = Role.query.filter_by(name=config.ROLE_USER).first()
        user.roles.append(role)

        ######################
        # Commit modifications
        db.session.add(user)
        db.session.commit()

        return self.response({'message': 'Profiling activated'})
