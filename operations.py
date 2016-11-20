#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Operations based on services pre-installed
"""

from operations import rethink2elastic as r2e
from operations import rethink
# from restapi import get_logger
# logger = get_logger(__name__)

#########################
# RETHINKDB

# rethink.build_zoom(force=True)
# rethink.medium_expo_thumbnail(force=False)
# rethink.fix_sources()
# rethink.convert_tiff()
# rethink.find_double_records()
rethink.some_operation()

# print("DEBUG"); exit(1)

#########################
# RETHINKDB 2 ELASTICSEARCH
r2e.make(only_xls=True)

#########################
print("Conversion completed")
exit(0)
