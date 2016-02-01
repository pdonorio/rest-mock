# -*- coding: utf-8 -*-

""" RDB most simple handler i could write """

import os
import time
import glob

# This Rethinkdb reference is already connected at app init
from rethinkdb import r, RqlDriverError

from flask import g
from flask.ext.restful import fields, marshal, request
from collections import OrderedDict
from .connections import Connection
from ... import get_logger

# Using docker, "**db**"" is my alias of the ReThinkDB container
RDB_HOST = "rdb"
RDB_PORT = 28015
# Models and paths
JSONS_PATH = 'models'
JSONS_EXT = '.json'
# Database and tables to use
APP_DB = "webapp"
DEFAULT_TABLE = "test"
TIME_COLUMN = 'latest_timestamp'
IP_COLUMN = 'latest_ipaddress'
USER_COLUMN = 'latest_user'

logger = get_logger(__name__)


###############################
def get_ip(ip=None):
    """ A quick (and dirty function) to get the IP from request """
# TO FIX
#   make one function/class from what you find in app.py
#   limit_remote_addr
#   Please fix me here:
# http://esd.io/blog/flask-apps-heroku-real-ip-spoofing.html
    if not request.headers.getlist("X-Forwarded-For"):
        ip = request.remote_addr
    else:
        ip = request.headers.getlist("X-Forwarded-For")[0]
    return ip


##########################################
# RethinkBD connection object
class RethinkConnection(Connection):
    """
    Connection for ReThinkDB.
    Based on the Borg design pattern, to optimize resources on
    opening connections for each request processed by Flask
    """

    def __init__(self, load_setup=False):
        """ My abstract method already connect by default """
        super(RethinkConnection, self).__init__(load_setup)

    # === Connect ===
    def make_connection(self, use_database):
        """
        This method implements the abstract interface
        of the Connection class which makes use of a **Singleton Borg**
        design pattern.
        See it yourself at: [[connections.py]]
        You will connect only once, using the same object.

        Note: authentication is provided with admin commands to server,
        after starting it up, using ssh from app container.
        Expecting the environment variable to contain a key.
        """
        params = {"host": RDB_HOST, "port": RDB_PORT}
        key = os.environ.get('KEYDBPASS') or None
        if key is not None:
            params["auth_key"] = key
            logger.info("Connection is pw protected")
        # else:
        #     logger.warning("Using no authentication")

        # Rethinkdb database connection
        try:
            # IMPORTANT! The chosen ORM library does not work if missing repl()
            # at connection time
            self._connection = r.connect(**params).repl()
            logger.debug("Created Connection")
        except RqlDriverError as e:
            logger.critical("Failed to connect RDB", e)
            return False

        logger.debug("Switching to database " + APP_DB)
        # Note: RDB db selection does not give error if the db does not exist
        self._connection.use(APP_DB)
        return self._connection

    def create_table(self, table=None, remove_existing=False):
        """ Creating a table if not exists,
        taking for Granted the DB already exists """

        if table in r.table_list().run():
            logger.debug("Table '" + table + "' already exists.")
            if remove_existing:
                r.table_drop(table).run()
                logger.info("Removed")
        else:
            r.table_create(table).run()
            logger.info("Table '" + table + "' created")


##########################################
# Need a pool of connections: http://j.mp/1yNP4p0
def try_to_connect():
    if g and "rdb" in g:
        return False
    try:
        logger.debug("Creating the rdb object")
        rdb = RethinkConnection()
        if g:
            g.rdb = rdb
    except Exception as e:
        logger.error("Cannot connect:\n'%s'" % e)
        return None
        # abort(hcodes.HTTP_INTERNAL_TIMEOUT,
        #     "Problem: no database connection could be established.")
    return True


##########################################
# RethinkBD base
class RDBdefaults(object):
    """ A class to apply defaults for rethinkdb operations """
    table = DEFAULT_TABLE
    db = APP_DB
    order = TIME_COLUMN

    def save_action_info(self, user=None):
        if user is None:
            user = 'UNKNOWN'
        return {
            TIME_COLUMN: time.time(),
            IP_COLUMN: get_ip(),
            USER_COLUMN: user
        }


##########################################
# RethinkBD class that can do queries
class RDBquery(RDBdefaults):
    """ An object to query Rethinkdb """

    schema = None
    template = None
    table_index = 'id'

    def get_query(self):
        return r.db(self.db)

    def get_table_query(self, table=None):
        if table is None:
            table = self.table
        # Build a base query: starting from default DB from RDBdefaults.
        base = r.db(self.db)
        # Create
        if table not in base.table_list().run():
            base.table_create(table).run()
        # Use the table
        return base.table(table)

    def execute_query(self, query, limit):
        count = 0
        data = {}

        if not query.is_empty().run():
            count = query.count().run()
            if limit > 0:
                query = query.limit(limit)
            # Note: fix time as i has to be converted if available
            # in original rethinkdb format
            data = query.run(time_format='raw')

        return count, list(data)

    def get_content(self, myid=None, limit=10, index='id'):
        """ For GET method, very simple """

        query = self.get_table_query()
        if self.table_index is not None:
            index = self.table_index

        # If need one element
        if myid is not None:
            query = query.get_all(myid, index=index)

        # Process
        return self.execute_query(query, limit)

    def insert(self, data, user=None):
#TOFIX:
# Find the user?
        # Prepare the query
        query = self.get_table_query()
        # Add extra info: (ip, timestamp, user)
        data['infos'] = self.save_action_info(user)
        # Execute the insert
        rdb_out = query.insert(data).run()
        # Get the id
#first_error?
        return rdb_out['generated_keys'].pop()

    def update(self, key, data, user=None):
        # Prepare the query
        query = self.get_table_query()
        # Add extra info: (ip, timestamp, user)
        data['infos'] = self.save_action_info(user)
        # Execute the insert
        rdb_out = query.update(key, data).run()
        print("\n\n\n", rdb_out, "\n\n\n")
        # Get the id
        return True

# # USELESS FOR REST MOCK API
#     def marshal(self, data, count=0):
#         return marshal(
#             {'data': data, 'count': count},
#             {'data': fields.Nested(self.schema), 'count': fields.Integer})

#     def nomarshal(self, data, count=0):
#         return OrderedDict({'data': data, 'count': count})
# # USELESS FOR REST MOCK API


##########################################
# Read model template
def load_models(extension=JSONS_EXT):
    """ How to look for json models for services API """
    return glob.glob(os.path.join(JSONS_PATH, "*") + extension)
