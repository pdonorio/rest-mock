# -*- coding: utf-8 -*-

"""
## RETHINKDB
# Convert old rethinkdb schema
# into new cool and fancy json automatic documents
"""

from __future__ import absolute_import
from restapi.resources.services.rethink import RethinkConnection, RDBquery
from restapi import get_logger

logger = get_logger(__name__)

# Tables
t1 = "stepstemplate"
t2 = "steps"
tin = "newsteps"


def convert_schema():

    # Connection
    RethinkConnection()
    # Query main object
    query = RDBquery()

    qt1 = query.get_table_query(t1)
    qt2 = query.get_table_query(t2)

    qtin = query.get_table_query(tin)
    qtin.delete().run()

    ############################
    # FIND
    data = qt1.group("step").run()
    for step in sorted(list(data)):
        new = {"step": None, "fields": None}
        myfilter = {'step': step}
        logger.info("*** STEP: %s" % step)

        # Single step elements
        element = list(qt2.filter(myfilter).run()).pop()
        new['step'] = {"num": step, "name": element['label'],
                       "desc": element['description']}

        # Singles steps fields
        tmp = {}
        fields = list(qt1.filter(myfilter).run())
        sorted_fields = sorted(fields, key=lambda k: k['position'])
        for row in sorted_fields:
            if 'extra' not in row:
                row['extra'] = None
            tmp[str(row['position'])] = {
                "name": row['field'],
                "position": row['position'],
                "required": row['required'],
                "type": row['type'],
                "options": row['extra'],
            }
        new["fields"] = tmp

        # INSERT
        logger.debug("To insert!\n%s" % new)
        qtin.insert(new).run()
        logger.info("Added row")
