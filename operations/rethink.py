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
from rethinkdb import r
from rethinkdb.net import DefaultCursorEmpty

logger = get_logger(__name__)
logger.setLevel(logging.DEBUG)

# Tables
t1 = "stepstemplate"
t2 = "steps"
t3 = "stepscontent"
t4 = "docs"
tin = "datakeys"
t2in = "datavalues"
t3in = "datadocs"

# Connection
RethinkConnection()
# Query main object
query = RDBquery()


def convert_docs():
    """ Convert Data needed for search """
    qt1 = query.get_table_query(t4)
    qtin = query.get_table_query(t3in)

    pkey = 'record'
    q = query.get_query()

    if t3in in list(q.table_list().run()):
        q.table_drop(t3in).run()
    q.table_create(t3in, primary_key=pkey).run()
    logger.info("Startup table '%s'" % t3in)

    # Query
    res = qt1.group('recordid').order_by('code').run()
    for record, rows in res.items():
        images = []
        for row in rows:
            images.append(row)

        # Insert
        qtin.insert({pkey: record, 'images': images}).run()
        logger.info("Insert of record '%s'" % record)


def convert_search():
    """ Convert Data needed for search """
    qt1 = query.get_table_query(t3)
    qt2 = query.get_table_query(tin)
    qtin = query.get_table_query(t2in)

    pkey = 'record'
    q = query.get_query()

    if t2in in list(q.table_list().run()):
        q.table_drop(t2in).run()
    q.table_create(t2in, primary_key=pkey).run()
    logger.info("Startup table '%s'" % t2in)

    # Query
    res = qt1.group('recordid').order_by('step').run()

    for record, rows in res.items():
        steps = []
        for row in rows:

            # Compose back the elements...
            index = 0
            elements = []
            for myhash in row['hashes']:
                # Query with lambda. COOL!
                cursor = qt2.filter(
                    lambda x: x['fields']['original_hash'].contains(myhash)
                    ).run()
                fields = []
#if not query.is_empty().run():
                try:
                    fields = cursor.next()['fields']
                except DefaultCursorEmpty:
                    logger.warning("No original hash for '%s'" % myhash)

                for field in fields:
                    if field['original_hash'] == myhash:
                        value = None
                        try:
                            value = row['values'][index]
                        except:
                            pass
                        elements.append({
                            'name': field['name'],
                            'position': field['position'],
                            'hash': field['original_hash'],
                            'value': value,
                        })
                        break
                index += 1

            # Create a sane JSON to contain all the data for one step
            steps.append({
                'step': row['step'],
                # Extra info
                'latest_db_info': {
# WHAT ABOUT TIMESTAMP CONVERSION ALSO?
                    'timestamp': row['latest_timestamp'],
                    'ip': row['latest_ipaddress'],
                    'user_id': row['user'],
                },
                'data': elements,
            })

        # Save the record
        qtin.insert({'record': record, 'steps': steps}).run()
        logger.info("Worked off document '%s'" % record)

    # # Create indexes
    # indexes = ['record']
    # existing_indexes = list(qtin.index_list().run())
    # for index in indexes:
    #     if index not in existing_indexes:
    #         qtin.index_create(index).run()
    #         logger.info("Added index '%s'" % index)


def check_indexes(table):

    q = query.get_table_query(table)
    existing_indexes = list(q.index_list().run())
    for index in existing_indexes:
        print(list(q.index_status(index).run()))


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
        element = []
        fields = list(qt1.filter(myfilter).run())
        sorted_fields = sorted(fields, key=lambda k: k['position'])
        for row in sorted_fields:
            if 'extra' not in row:
                row['extra'] = None

            element.append({
                "name": row['field'],
                "position": row['position'],
                "required": row['required'],
                "type": row['type'],
                "options": row['extra'],
                "original_hash": row['hash'],
            })

        # A whole step
        new["fields"] = element

        # INSERT
        logger.debug("To insert!\n%s" % new)
        qtin.insert(new).run()
        logger.info("Added row")


def test_query():
    """ test queries on rdb """
    q = query.get_table_query(t2in)

    # http://stackoverflow.com/a/34647904/2114395
    cursor = q \
        .concat_map(
            lambda doc: doc['steps']
            .concat_map(lambda step: step['data']
                        .concat_map(lambda data:
                        [{'record': doc['record'], 'step': data}]))) \
        .filter(lambda doc:
                doc['step']['value'].match('mog').
                and_(doc['step']['name'].match('Numero de page'))) \
        .run()

    for obj in cursor:
        print("TEST", obj)
        exit(1)

# #TEST1
#     cursor = q \
#         .concat_map(
#             lambda x: x['steps']['data'].map(
#                 lambda item: item['value'])
#         ) \
#         .run()
#     for obj in cursor:
#         print("TEST", obj)
#         exit(1)
#     print(list(cursor))
#     exit(1)

#WORKING FOR RECOVERING DATA
    cursor = q \
        .concat_map(r.row['steps']) \
        .filter(
            lambda row: row['step'] == 3
            ) \
        .concat_map(r.row['data']) \
        .filter(
            lambda row: row['position'] == 1
        ).pluck('value').distinct()['value'].run()
    print(list(cursor))


def convert_schema():
    """ Do all ops """
    test_query()
    print("DEBUG"); exit(1);
    convert_submission()
    # check_indexes(t2in)
    convert_search()
    convert_docs()
