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

# rethink.fix_sources()
# rethink.convert_tiff()
# rethink.find_double_records()
rethink.build_zoom(force=False)
# print("Exit DEBUG"); exit(1)

# rethink.medium_expo_thumbnail(force=False)
# rethink.some_operation()

#########################
# RETHINKDB 2 ELASTICSEARCH
r2e.make(only_xls=True)

#########################
print("Conversion completed")
exit(0)
