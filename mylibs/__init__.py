#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" My python libraries """

import os

# From the directory where the app is launched
PROJECT_DIR = '.'
CONFIG_DIR = 'confs'

LOG_CONFIG = os.path.join(PROJECT_DIR, CONFIG_DIR, 'logging_config.ini')

# ####################################
# LOGGING
#http://docs.python-guide.org/en/latest/writing/logging/

# Set default logging handler to avoid "No handler found" warnings.
import logging
from logging.config import fileConfig

try:  # Python 2.7+
    from logging import NullHandler
except ImportError:
    class NullHandler(logging.Handler):
        def emit(self, record):
            pass
#logging.getLogger(__name__).addHandler(NullHandler())

from mylibs import LOG_CONFIG
fileConfig(LOG_CONFIG)
