#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Operations based on services pre-installed
"""

from __future__ import absolute_import

# from restapi import get_logger
# logger = get_logger(__name__)

#########################
# RETHINKDB
from operations import rethink
rethink.convert_schema()
