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
# RETHINKDB
from operations import rethink

rethink.some_operation()
# rethink.rebuild_zoom()
rethink.medium_expo_thumbnail(force=False, rebuild_zoom=True)
print("Skip the elastic index rebuilding"); exit(0)
# rethink.expo_operations()
# rethink.convert_tiff()

#########################
# RETHINKDB 2 ELASTICSEARCH
r2e.make()
print("Conversion completed")
exit(0)
