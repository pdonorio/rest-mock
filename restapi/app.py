#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Flask app creation
"""

from . import myself, lic, get_logger
from .server import create_app
import argparse

__author__ = myself
__copyright__ = myself
__license__ = lic

logger = get_logger(__name__)

#############################
# Command line arguments
arg = argparse.ArgumentParser(description='REST API server based on Flask')
arg.add_argument("--no-security", action="store_false", dest='security',
                 help='force removal of login authentication on resources')
arg.set_defaults(security=True)
args = arg.parse_args()
if not args.security:
    logger.warning("No security enabled!")

#############################
# BE FLASK
microservice = create_app(name='REST', enable_security=args.security)
# We are now ready
logger.info("*** Our REST API server/app is ready ***")
# Some code may take this app from here
