#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Flask app creation
"""

from . import myself, lic, get_logger
from .server import create_app
import argparse
import time

__author__ = myself
__copyright__ = myself
__license__ = lic

logger = get_logger(__name__)

#############################
# Command line arguments
arg = argparse.ArgumentParser(description='REST API server based on Flask')
arg.add_argument("--no-security", action="store_false", dest='security',
                 help='force removal of login authentication on resources')
arg.add_argument("--debug", action="store_true", dest='debug',
                 help='enable debugging mode')
arg.set_defaults(security=True, debug=False)
args = arg.parse_args()
if args.debug:
    logger.warning("Enabling DEBUG mode")
    time.sleep(1)
if not args.security:
    logger.warning("No security enabled! Are you sure??")
    time.sleep(1)

#############################
# BE FLASK
app = create_app(name='API', enable_security=args.security, debug=args.debug)
# We are now ready
logger.info("*** Our REST API server/app is ready ***")
# Some code may take this app from here
