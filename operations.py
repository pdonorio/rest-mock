#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Operations based on services pre-installed
"""

from __future__ import absolute_import

from operations import rethink2elastic as r2e
# from restapi import get_logger
# logger = get_logger(__name__)

#########################
# Add translations?
from operations import rethink
rethink.enable_translations()

#########################
# RETHINKDB 2 ELASTICSEARCH
r2e.make()
print("Conversion completed")
exit(0)

# #########################
# # RETHINKDB
# from operations import rethink
# rethink.convert_schema()
