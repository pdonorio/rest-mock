# -*- coding: utf-8 -*-

""" RDB most simple handler i could write """

import os
import time
import glob
import commentjson as json

# This Rethinkdb reference is already connected at app init
from rethinkdb import r, RqlDriverError

from flask import g  # , url_for, redirect
from flask.ext.restful import request  # , fields, marshal
from .connections import Connection
from ..base import ExtendedApiResource
from ... import htmlcodes as hcodes
from ...marshal import convert_to_marshal
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
ACTION_COLUMN = 'operation'
TIME_COLUMN = 'timestamp'
IP_COLUMN = 'ipaddress'
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


def wait_for_connection():
    """ Wait for rethinkdb connection at startup? """

    counter = 0
    sleep_time = 1
    testdb = True

    while testdb:
        try:
            rdb = r.connect(host=RDB_HOST, port=RDB_PORT)
            logger.info("Rethinkdb: available")
            testdb = False
            # Need a pool of connections: http://j.mp/1yNP4p0
            if g and "rdb" not in g:
                g.rdb = rdb
        except RqlDriverError:
            logger.warning("Rethinkdb: Not reachable yet")
        counter += 1
        if counter % 10 == 0:
            sleep_time += sleep_time
        time.sleep(sleep_time)

    return True


##########################################
def try_to_connect():
    if g and "rdb" in g:
        return False
    try:
        logger.debug("Creating the rdb object")
        rdb = RethinkConnection()
        # Need a pool of connections: http://j.mp/1yNP4p0
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

    def save_action_info(self, document, action='record_creation'):

        if not isinstance(document, dict):
            logger.warning("The element to insert is not a document")
            return document

        key = "logs"
# RECOVER THE USER FROM FLASK!
# Recover from token? # Somewhere with Flask security
        user = None
        if user is None:
            user = 'UNKNOWN'

        log = {
            TIME_COLUMN: time.time(),
            ACTION_COLUMN: action,
            IP_COLUMN: get_ip(),
            USER_COLUMN: user
        }
        if key not in document:
            document[key] = []
        document[key].append(log)

        return document


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

    def list_tables(self):
        return list(self.get_query().table_list().run())

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

    def insert(self, data, table=None):
        # Prepare the query
        query = self.get_table_query(table)
        # Add extra info: (ip, timestamp, user, action)
        # Execute the insert
        rdb_out = query.insert(self.save_action_info(data)).run()

        logger.debug("Debugging ReThinkDB insert: %s" % rdb_out)

        # Handling error
        key = 'errors'
        if key in rdb_out and rdb_out[key] > 0:
            error = "Failed to insert"
            key = 'first_error'
            if key in rdb_out:
                error = rdb_out[key]
            raise BaseException(error)

        # Get the id
        key = 'generated_keys'
        if key in rdb_out:
            return rdb_out['generated_keys'].pop()
        return 'Unknown ID'

    def update(self, key, data, table=None):
        # Prepare the query
        query = self.get_table_query(table)
        # Execute the insert
        rdb_out = query.update(key, self.save_action_info(data)).run()
        print("\n\n\nUPDATE!", rdb_out, "\n\n\n")
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


##########################################
def schema_and_tables(fileschema):
    """
    This function can recover basic data for my JSON resources
    """
    template = None
    with open(os.path.join(JSONS_PATH, fileschema + JSONS_EXT)) as f:
        template = json.load(f)
    reference_schema = convert_to_marshal(template)
    label = os.path.splitext(
        os.path.basename(fileschema))[0].lower()

    return label, template, reference_schema


#####################################
# Base implementation for methods?
class BaseRethinkResource(ExtendedApiResource, RDBquery):
    """ The json endpoint in a rethinkdb base class """

    def get(self, data_key=None):
        """
        Obtain main data.
        Obtain single objects.
        Filter with predefined queries.
        """

        # Check arguments
        limit = self._args['perpage']
# // TO FIX: use it!
        current_page = self._args['currentpage']

        return self.get_content(data_key, limit)

    def check_valid(self, json_data):
        """ Verify if the json data follows the schema """
        # Check if dictionary and not empty
        if not isinstance(json_data, dict) or len(json_data) < 1:
            return False
        # Check template
        for key, obj in json_data.items():
            if key not in self.schema:
                return False
        # All fine here
        return True

    def post(self):

        json_data = self.get_input()
        if not self.check_valid(json_data):
            logger.warning("Not a valid template")
            return self.template, hcodes.HTTP_BAD_REQUEST

        # marshal_data = marshal(json_data, self.schema, envelope='data')
        myid = self.insert(json_data)

        #####################
        # redirect to GET method of this same endpoint, with the id found
        #address = url_for(self.table, data_key=myid)
        #return redirect(address)
        # or return the key
        return myid
        #####################

    def put(self, id, index='id'):

        json_data = self.get_input()
        if 'id' in json_data:
            json_data.pop('id')

        if not self.check_valid(json_data):
            logger.warning("Not a valid template")
            return self.template, hcodes.HTTP_BAD_REQUEST

        changes = self.get_table_query().get_all(id, index=index) \
            .update(json_data, return_changes=True).run()
        # Contains all changes applied
        return changes

    def delete(self, id, index='id'):
        """ Remove an element from database (based on primary key) """

        out = self.get_table_query().get_all(id, index=index) \
            .delete().run()
        if out['deleted']:
            logger.debug("Removed record '%s'" % id)
        else:
            return id, hcodes.HTTP_SERVICE_UNAVAILABLE
        return True
