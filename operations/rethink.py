# -*- coding: utf-8 -*-

"""
## RETHINKDB
# Convert old rethinkdb schema
# into new cool and fancy json automatic documents
"""

from __future__ import absolute_import
import logging
from restapi.resources.services.rethink import RethinkConnection, RDBquery
from restapi import get_logger

logger = get_logger(__name__)
logger.setLevel(logging.DEBUG)

# Tables
t1 = "stepstemplate"
t2 = "steps"
tin = "newsteps"

t3 = "stepscontent"
t2in = "newstepscontent"

# Connection
RethinkConnection()
# Query main object
query = RDBquery()


def convert_search():
    """ Convert Data needed for search """
    qt1 = query.get_table_query(t3)
    qt2 = query.get_table_query(tin)
    qtin = query.get_table_query(t2in)
    qtin.delete().run()

    # DO
    data = {}
    for row in qt1.run():
        print(row)
        for myhash in row['hashes']:
            print(myhash)
            results = qt2.filter(
                lambda x: x['fields']['original_hash'].contains(myhash)
                ).run()
            print([x['fields'] for x in results].pop())
            # check = qt2.filter({'fields':
            #     lambda x: x['original_hash'] == myhash }).run()
            # if check:
            #     for x in check:
            #         print(x)#, x['name'], x['step'])
            # else:
            #     print("Cannot find", myhash)
            #     exit(1)
            # #print(qt2.filter({'hash': myhash}).run())
            exit(1)
        exit(1)


def convert_submission():
    """ Convert schema for Steps Submission """

    qt1 = query.get_table_query(t1)
    qt2 = query.get_table_query(t2)
    qtin = query.get_table_query(tin)
    qtin.delete().run()

    # DO
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
        tmp = []
        fields = list(qt1.filter(myfilter).run())
        sorted_fields = sorted(fields, key=lambda k: k['position'])
        for row in sorted_fields:
            if 'extra' not in row:
                row['extra'] = None

            tmp.append({
                # 'position': row['position'],
                # 'data': {
                    "name": row['field'],
                    "position": row['position'],
                    "required": row['required'],
                    "type": row['type'],
                    "options": row['extra'],
                    "original_hash": row['hash'],
                # }
            })

        # A whole step
        new["fields"] = tmp

        # INSERT
        logger.debug("To insert!\n%s" % new)
        qtin.insert(new).run()
        logger.info("Added row")


def convert_schema():
    """ Do all ops """
    #convert_submission()
    convert_search()
