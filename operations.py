# -*- coding: utf-8 -*-

"""
Operations based on services pre-installed
"""

from __future__ import absolute_import

# from restapi import get_logger
# logger = get_logger(__name__)

# import re
# string = "there is (1,some) (2,repeat) (3,iscion)"
# pattern = r"(there is)(?: \([0-9]+,([^\)]+)\))+"
# m = re.search(pattern, string)
# print(m.groups())
# exit(1)

#########################
# RETHINKDB
from operations import rethink
rethink.convert_schema()
