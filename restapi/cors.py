# -*- coding: utf-8 -*-

"""
Main server factory.
We create all the components here!
"""

from __future__ import division, absolute_import
from . import myself, lic, get_logger

# Handle cors...
from flask_cors import CORS

__author__ = myself
__copyright__ = myself
__license__ = lic

logger = get_logger(__name__)


# ####################################
# Allow cross-domain requests
# e.g. for JS and Upload

cors = CORS(
    # resources={r"/api/*": {"origins": "*"}},
    headers=['Content-Type', 'Authorization'],
    methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH'],  # , 'OPTIONS'],
    )

# You may want to read more:
# http://stackoverflow.com/q/26980713/2114395
logger.warning("Creating CORS")

# # WARNING: in case 'cors' write too much, you could fix it like this
# import logging
# corslogger = logging.getLogger('.server.cors')
# corslogger.setLevel(logging.WARNING)
