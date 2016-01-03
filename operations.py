# -*- coding: utf-8 -*-

"""
Operations based on services pre-installed
"""

from __future__ import absolute_import
from operations import rethink

# from restapi import get_logger
# logger = get_logger(__name__)

#########################
# RETHINKDB
rethink.convert_schema()
