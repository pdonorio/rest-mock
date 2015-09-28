#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" My python libraries """

import os
from confs.config import LOGGING_CONFIG_FILE, REST_CONFIG_FILE, DEBUG

# From the directory where the app is launched
PROJECT_DIR = '.'
CONFIG_DIR = 'confs'
LOG_CONFIG = os.path.join(PROJECT_DIR, CONFIG_DIR, LOGGING_CONFIG_FILE)
REST_CONFIG = os.path.join(PROJECT_DIR, CONFIG_DIR, REST_CONFIG_FILE)

# LOGGING
#http://docs.python-guide.org/en/latest/writing/logging/
import logging
if DEBUG:
    LOG_LEVEL = logging.DEBUG
else:
    LOG_LEVEL = logging.INFO
# Set default logging handler to avoid "No handler found" warnings.
from logging.config import fileConfig

try:  # Python 2.7+
    from logging import NullHandler
except ImportError:
    class NullHandler(logging.Handler):
        def emit(self, record):
            pass
logging.getLogger(__name__).addHandler(NullHandler())
# Read from file configuration
fileConfig(LOG_CONFIG)
# A function to recover the right logger and set a proper specific level
def get_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(LOG_LEVEL)
    return logger
