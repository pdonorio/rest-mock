# -*- coding: utf-8 -*-

"""
## RETHINKDB
# Convert old rethinkdb schema
# into new cool and fancy json automatic documents

r.connect(host='rdb').repl()
v = r.db('webapp')
a = v.table('datadocs').update({"type":'documents'}).run()

"""

from __future__ import absolute_import
import os
import shutil
import glob
from restapi.resources.services.rethink import RethinkConnection, RDBquery
from restapi.resources.services.uploader import ZoomEnabling
from restapi.resources.utilities import split_and_html_strip
from restapi.resources.custom.docs import image_destination
from restapi import get_logger
from rethinkdb import r
from rethinkdb.net import DefaultCursorEmpty
from datetime import datetime
from elasticsearch import Elasticsearch
from confs.config import args, UPLOAD_FOLDER

import logging
logger = get_logger(__name__)
logger.setLevel(logging.DEBUG)

ES_HOST = {"host": "el", "port": 9200}
EL_INDEX = "autocomplete"
STEPS = {}
# TESTING = False
TESTING = True

# Tables
t1 = "stepstemplate"
t2 = "steps"
t3 = "stepscontent"
t4 = "docs"
tin = "datakeys"
t2in = "datavalues"
t3in = "datadocs"
t4in = 'datadmins'

# Connection
RethinkConnection()
# Query main object
query = RDBquery()

######################
# Parameters
if args.rm:
    logger.info("Remove previous data")
    tables = query.list_tables()
    if tin in tables:
        query.get_query().table_drop(tin).run()
    if t2in in tables:
        query.get_query().table_drop(t2in).run()
    if t3in in tables:
        query.get_query().table_drop(t3in).run()


#################################
# MAIN
#################################
def convert_schema():
    """ Do all ops """

    ######################
    # Make tests
    if TESTING:
        test_query()
        # test_el()

    ######################
    # Conversion from old structure to the new one
    tables = query.list_tables()

    if tin not in tables:
        convert_submission()
    if t2in not in tables:
        convert_search()
    if t3in not in tables:
        convert_docs()
    # remove pending files...
    convert_pending_images()

    # check_indexes(t2in)


def check_doubles():
    q = query.get_table_query('datavalues')
    for record in q.run():
        steps = {}

        wrong = 0
        for step in record['steps']:
            key = step['step']
            if key not in steps:
                steps[key] = []
            steps[key].append(step['data'])

            if len(steps[key]) > 1:
                wrong = key

        if wrong > 0:
            logger.info("Wrong is %s in %s" % (wrong, record['record']))
            index = 0
            to_be_removed = []
            original = len(record['steps'])
            for step in record['steps']:
                if step['step'] == wrong:
                    to_be_removed.append(index)
                index = index + 1
            for element in to_be_removed[::-1]:
                del record['steps'][element]
            final = len(record['steps'])
            logger.debug("From %s to %s" % (original, final))

            q.get(record['record']).replace(record).run()


#################################
#################################
def check_translations():

    q2 = query.get_table_query('datadocs')
    for record in q2.run():

        if record['type'] != 'documents':
            continue

        # q = query.get_table_query('datavalues')
        # print(record)
        # data = element['steps'][0]['data']
        # print("\n\nTEST", data[0]['value'])
        # exit(1)

        images = record.pop('images')
        if len(images) < 1:
            continue
        image = images.pop()
        if 'translations' in image:
            x = query.get_table_query('datavalues').get(record['record']).run()
            for step in x['steps']:
                if step['step'] == 1:
                    for y in step['data']:
                        if y['position'] == 1:
                            print(y['value'])
                            break
                    break


def expo_operations():

    convert = {

        'position': 'position',
        'title': 'titre',
        # 'name': 'nom', # REMOVED
        'author': 'auteur(s)',

        # mix them as 'date et lieu de réalisation'
        'date': 'date',
        'place': 'lieu',

        'book': 'source',
        'material': 'matériaux',
        'description': 'texte',

    }

    # q1 = query.get_table_query('expo')
    q2 = query.get_table_query('datadocs')

    for single in q2.run():
        if 'details' not in single or len(single['details']) < 2:
            continue
        logger.debug("Updating %s" % single['record'])
        # print(single['details'])
        new = {}
        for key, value in single['details'].items():
            # print(key, value)
            if key in convert:
                new[convert[key]] = value

        index = 'date et lieu de réalisation'
        if 'date' in single['details'] or 'place' in single['details']:
            new[index] = ""
        if 'date' in single['details']:
            new[index] += single['details']['date']
        if 'place' in single['details']:
            if new[index].strip() != '':
                new[index] += ", "
            new[index] += single['details']['place']

        # print("\n\n", new)
        single['details'] = new
        # print("\n\n", single)
        q2.get(single['record']).replace(single).run()
        # import time
        # time.sleep(3)
    exit(1)


#################################
#################################

def rebuild_zoom():
# def convert_tiff():

    import re
    pattern = re.compile("^[0-9]+$")
    zoomer = ZoomEnabling()

    q = query.get_table_query(t3in)
    for record in q.run():

        if record['type'] != 'documents':
            continue

        # q = query.get_table_query('datavalues')
        # print(record)
        # data = element['steps'][0]['data']
        # print("\n\nTEST", data[0]['value'])
        # exit(1)

        images = record.pop('images')
        if len(images) < 1:
            continue
        image = images.pop()

        ##################
        # FIX ZOOM for files like [0-9]+.jpg

        # LIMIT?
        # print("TEST", image)
        # match = pattern.match(image['code'])
        # if match is None:
        #     continue

        ##################
        abs_file = os.path.join(UPLOAD_FOLDER, image['filename'])

        # Remove zoomified directory
        filebase, fileext = os.path.splitext(abs_file)
        if os.path.exists(filebase):
            try:
                shutil.rmtree(filebase)
                logger.debug("Removed dir '%s' " % filebase)
            except Exception as e:
                logger.critical("Cannot remove zoomified:\n '%s'" % str(e))

        logger.debug("Converting %s" % abs_file)
        if not zoomer.process_zoom(abs_file):
            raise BaseException("Failed to zoom file '%s'" % image['filename'])
        logger.info("Zoomed image '%s'" % image['filename'])

        # ##################
        # # FIX TIFF
        # if not image['filename'][-4:] == '.tif':
        #     continue

        # path = os.path.join('/uploads', image['filename'])
        # if not os.path.exists(path):
        #     raise BaseException("Cannot find registered path %s" % path)

        # newpath = path.replace('.tif', '.jpg')

        # # Convert tif to jpg
        # from plumbum.cmd import convert
        # convert([path, newpath])
        # logger.info("Converted TIF to %s" % newpath)

        # # Update
        # image['filename'] = image['filename'].replace('.tif', '.jpg')

        # # key = 'transcriptions_split'
        # # if key in image:
        # #     image.pop(key)
        # # # image['translation'] = False
        # # # image['language'] = '-'
        # # record['images'] = [image]
        # # changes = q.get(record['record']).replace(record).run()

        # record['images'] = [image]
        # changes = q.get(record['record']).replace(record).run()
        # print("Changes", changes)
        # logger.debug("Updated %s" % record['record'])

        # # import time
        # # time.sleep(5);


def convert_pending_images():
    """ Find images not linked to documents """

    q = query.get_table_query(t3in)
    cursor = q['images'] \
        .map(
            lambda images:
                {'file': images['filename'], 'record': images['recordid']}
         ).distinct().run()

    logger.info("Obtained pending data")
    images = glob.glob(os.path.join(UPLOAD_FOLDER, "*.jpg"))

    # Missing
    for obj in list(cursor):

        # Check if exists
        absfile = os.path.join(UPLOAD_FOLDER, obj['file'].pop())
        if absfile in images:
            images.pop(images.index(absfile))
        elif len(obj['record']) > 0:
            # Remove images which are not physical uploaded
            q.get(obj['record'].pop()).delete().run()
            logger.debug("Removed pending file '%s' from table", absfile)

# // TO FIX:
# MAKE A TABLE OF DRAFTS INSTEAD

    # REMOVE
    # # Remove physical images which do not belong to any record?
    # for image in images:
    #     os.unlink(image)
    #     logger.debug("Removed unused image '%s'" % image)
    # REMOVE


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
    key = 'transcriptions'
    for record, rows in res.items():
        images = []
    # Check images
        for row in rows:
            if key in row:
                words = set()
    # Fix transcriptions
                for trans in row[key]:
                    words = words | split_and_html_strip(trans)
                row[key+'_split'] = list(words)
            images.append(row)

        # Insert
        qtin.insert({
            pkey: record,
            'images': images,
            'type': image_destination({})
        }).run()
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

    # # Elasticsearch magic
    # print("Elasticsearch and indexes")
    # es = Elasticsearch(hosts=[ES_HOST])
    # es.indices.delete(index=EL_INDEX, ignore=[400, 404])
    # es.indices.create(index=EL_INDEX, ignore=400)
    # #es.indices.refresh(index=EL_INDEX)

    for record, rows in res.items():
        steps = []
        title = None

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
                        if field['position'] == 1:
                            title = value
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

# PLUG ELASTICSEARCH SOMEWHERE IN HERE
        doc = {
            'category': STEPS[row['step']],
            'text': title,
            'timestamp': datetime.now(),
        }
# # TO FIX?
#         #print(doc)
#         es.index(index=EL_INDEX, doc_type='normal', body=doc)
#         #print("DEBUG EXIT"); exit(1)


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
        tmp = new['step']
        STEPS[tmp['num']] = tmp['name']
    print(STEPS)


def test_query():
    """ test queries on rdb """

    ###################################################
    # Try optimization with seconday index

    """
    q = query.get_table_query(t3in)
    # cursor = q \
    #     .concat_map(lambda obj: obj['images']['transcriptions_split']) \
    #     .limit(2) \
    #     .run()

    # print("TEST", list(cursor))
    # exit(1)

    q = query.get_table_query(t2in)

    cursor = q \
        .concat_map(lambda obj: obj['steps']
            .concat_map(lambda steps: steps['data']
                .filter(lambda row:
                    (row['position'] == 1)
                    & (r.expr(["", None]).contains(row['value']).not_())
                )
                .map(lambda data:
                    {
                        'step': steps['step'],
                        'position': data['position'],
                        'value': data['value'],
                    }))
            .without('position')
            .filter(lambda row: row['value'].match('(?i)^c')) \
        ) \
        .limit(7).run()
    print("TEST", list(cursor))
    exit(1)
    """

    index = "title"
    search = "Limoges_33"
    q = query.get_table_query(t2in)

    # test = q.concat_map(
    #     lambda doc: doc['steps'].concat_map(
    #         lambda step: step['data']['value'])) \
    #     .run()
    # print("TEST", test)
    # exit(1)

    if index in q.index_list().run():
        print("Dropping")
        q.index_drop(index).run()
    print("Creating")
    q.index_create(index,
        lambda doc: doc['steps'].concat_map(
        lambda step: step['data']['value']),
        multi=True
        ) \
        .run()
    print("Waiting")
    q.index_wait(index).run()
    print("Done")

    print("Status", q.index_status().run())
    cursor = q.get_all(search, index=index).run()
    print("Test key:\n", list(cursor))
    exit(1)

    ###################################################
    document = '5fc8d3f4-59ee-43ca-9543-6241bb820882'
    extra = {
        'data': [
            {'value': 'Test', 'name': 'Personnages', 'position': 1, 'hash': '035ca5c7'},
            {'value': 'From paolo', 'name': 'Artistes', 'position': 2, 'hash': '01b1020a'}
        ],
        'latest_db_info':
            {'timestamp': 1458124102.565326, 'user_id': '1a33400a', 'ip': '109.89.122.137'},
        'step': 4
    }

    q = query.get_table_query(t2in)
    cursor = q.get(document).run()
    cursor['steps'].append(extra)
    print(cursor, type(cursor))

    changes = q.get(document).replace(cursor).run()
    #     .update(lambda row: row['steps'].append(extra))
    print(changes)
    # print(cursor.run())
    # print(list(cursor.run()))
    print("DEBUG"); exit(1)

    ##################################

    q = query.get_table_query(t4in)
    cursor = q \
        .filter({'type': 'welcome'}).without('type') \
        .eq_join("id", r.table(t3in), index="record") \
        .zip() \
        .filter({'type': 'welcome'})
    print(list(cursor.run()))
    print("DEBUG"); exit(1)

    cursor = q \
        .concat_map(
            lambda doc: doc['images'].has_fields(
                {'transcriptions': True}).map(
                    lambda image: {
                        'word': image['transcriptions_split'],
                        'record': doc['record'],
                    }
                )).distinct() \
        .filter(lambda mapped: mapped['word'].contains('grati')) \
        .run()

    # print(len(list(cursor)))
    # exit(1)
    for obj in cursor:
        print("TEST", obj)
        exit(1)
    exit(1)

    # # http://stackoverflow.com/a/34647904/2114395
    # cursor = q \
    #     .concat_map(
    #         lambda doc: doc['steps']
    #         .concat_map(lambda step: step['data']
    #                     .concat_map(lambda data:
    #                     [{'record': doc['record'], 'step': data}]))) \
    #     .filter(lambda doc:
    #             doc['step']['value'].match('mog').
    #             and_(doc['step']['name'].match('Numero de page'))) \
    #     .run()

    # for obj in cursor:
    #     print("TEST", obj)
    #     exit(1)

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


def test_el():
    print("TEST")
    es = Elasticsearch(hosts=[ES_HOST])
    print(es)

    # doc = {
    #     'author': 'kimchy',
    #     'text': 'Elasticsearch: cool. bonsai cool.',
    #     'timestamp': datetime.now(),
    # }
    # res = es.index(index="test-index", doc_type='tweet', id=1, body=doc)
    # print(res['created'])

    # Note:
    # Refresh indices at login startup!!!
    es.indices.refresh(index="test-index")

    res = es.get(index="test-index", doc_type='tweet', id=1)
    print(res['_source'])

    #es.search(index='posts', q='author:"Benjamin Pollack"')

    exit(1)
