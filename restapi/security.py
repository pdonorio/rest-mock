#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Main server factory.
We create all the components here!
"""

from __future__ import division, print_function, absolute_import
from . import myself, lic, get_logger

from flask_admin import Admin

__author__ = myself
__copyright__ = myself
__license__ = lic

logger = get_logger(__name__)

####################################
# Admininistration
admin = Admin(name='Adminer', template_mode='bootstrap3')
logger.debug("Flask: creating Admininistration")
