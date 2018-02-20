#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-

"""
Operations based on services pre-installed
"""

import sys
from operations import rethink2elastic as r2e
from restapi import get_logger
log = get_logger(__name__)

lexique = False
if len(sys.argv) > 1:
    lexique = bool(int(sys.argv[1]))

# if True:
#     import time
#     time.sleep(10000)

#########################
# RETHINKDB

# if True:
#     from operations import rethink
#     # rethink.fix_sources()
#     # rethink.convert_tiff()
#     # rethink.find_double_records()
#     # rethink.build_zoom(force=False)
#     # rethink.medium_expo_thumbnail(force=False)
#     # rethink.fix_languages()
#     # rethink.find_word(['sucre', 'atlas', 'nympha'])
#     rethink.some_operation()
#     exit(1)

#########################
# RETHINKDB 2 ELASTICSEARCH

# r2e.make()
if lexique:
    log.info("Do only lexique")
    r2e.make(only_xls=True)
else:
    log.info("Rebuild elasticsearch indexes")
    r2e.make(skip_lexique=True)

#########################
log.info("Operation: completed")
exit(0)
