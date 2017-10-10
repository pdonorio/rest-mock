#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-

"""
Operations based on services pre-installed
"""

import sys
from operations import rethink2elastic as r2e
from operations import rethink
from restapi import get_logger
log = get_logger(__name__)

skip_lexique = True
if len(sys.argv) > 1:
    skip_lexique = bool(int(sys.argv[1]))

#########################
# RETHINKDB

# rethink.fix_sources()
# rethink.convert_tiff()
# rethink.find_double_records()
# rethink.build_zoom(force=False)
# rethink.medium_expo_thumbnail(force=False)
# rethink.fix_languages()
rethink.some_operation()
# rethink.find_word(['sucre', 'atlas', 'nympha'])
# exit(1)

#########################
# RETHINKDB 2 ELASTICSEARCH
log.info("Skipping Lexique creation? %s", skip_lexique)

# r2e.make()
# FIXME
r2e.make(skip_lexique=True)
# r2e.make(only_xls=True)

#########################
print("Conversion completed")
exit(0)
