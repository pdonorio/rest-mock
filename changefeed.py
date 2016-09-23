#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PoC for subscriptions with rethinkdb tables and documents
https://rethinkdb.com/docs/changefeeds/python/
"""

import rethinkdb as r
import sys
from beeprint import pp

# variables
host = 'rdb'
db = 'mydb'
table = 'mytable'

# connect and create
r.connect(host=host).repl()
if db not in r.db_list().run():
    r.db_create(db).run()
if table not in r.db(db).table_list().run():
    r.db(db).table_create(table).run()

# implement actions
query = r.db(db).table(table)
if len(sys.argv) > 1:
    command = sys.argv[1]
    if command == 'changefeed':
        try:
            for change in query.changes().run():
                print("Subscription update!")
                pp(change)
        except Exception as e:
            print("Table removed or connection aborted")
    elif command == 'insert':
        query.insert({'key1': 'value1', 'key2': 'value2'}).run()
    elif command == 'update':
        query.filter({'key1': 'value1'}).update({'key1': 'UPDATED!'}).run()
    elif command == 'clear':
        r.db_drop(db).run()
