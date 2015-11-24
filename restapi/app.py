#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Flask app creation
"""

from . import myself, lic, get_logger
from .server import create_app

__author__ = myself
__copyright__ = myself
__license__ = lic

logger = get_logger(__name__)

#############################
# BE FLASK
microservice = create_app()
# We are now ready
logger.info("*** Our REST API server/app is ready ***")
# Some code may take this app from here
