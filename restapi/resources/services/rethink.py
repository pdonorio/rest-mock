# -*- coding: utf-8 -*-

""" RDB most simple handler i could write """

import os
import time
import glob
import json
# This Rethinkdb reference is already connected at app init
from rethinkdb import r, RqlDriverError
from flask import redirect, g
from flask.ext.restful import fields, Resource, marshal, request
from flask.ext.restful import url_for
from ...marshal import convert_to_marshal
from ... import htmlcodes as hcodes
from ... import get_logger
from .connections import Connection

# Models and paths
JSONS_PATH = 'models'
JSONS_EXT = 'json'
# Using docker, "**db**"" is my alias of the ReThinkDB container
RDB_HOST = "db"
# Docker forwarding port system var (otherwise use standard rethinkdb port)
RDB_PORT = os.environ.get('DB_PORT_28015_TCP_PORT') or 28015
# Database and tables to use
APP_DB = "webapp"
DEFAULT_TABLE = "test"
TIME_COLUMN = 'latest_timestamp'
IP_COLUMN = 'latest_ipaddress'
USER_COLUMN = 'latest_user'

logger = get_logger(__name__)


###############################
# TO FIX
#   make one function/class from what you find in app.py
#   limit_remote_addr
#   Please fix me here:
# http://esd.io/blog/flask-apps-heroku-real-ip-spoofing.html
def get_ip():
    ip = None
    if not request.headers.getlist("X-Forwarded-For"):
        ip = request.remote_addr
    else:
        ip = request.headers.getlist("X-Forwarded-For")[0]
    return ip


class RDBdefaults(object):
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
# ## RethinkBD quick class
class RDBquery(RDBdefaults):
    """ An object to query Rethinkdb """

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

    def get_content(self, myid=None):

        data = {}
        query = self.get_table_query()
        if myid is not None:
            query = query.get_all(myid, index='id')

        count = 0
        if not query.is_empty().run():
            count = query.count().run()
            data = query.run()

        # # Recover only one document
        # document = query.get(myid).run()
        # if document is not None:
        #     document.pop('id')

        return (count, list(data))

    def insert(self, data, user=None):
        # Prepare the query
        query = self.get_table_query()
        # Add extra info: (ip, timestamp, user)
        data['infos'] = self.save_action_info(user)
        # Execute the insert
        rdb_out = query.insert(data).run()
        # Get the id
        return rdb_out['generated_keys'].pop()


##########################################
# The generic resource
class RethinkResource(Resource, RDBquery):
    """ The json endpoint to rethinkdb class """

    schema = None
    template = None

    def get(self, data_key=None):
        (count, data) = self.get_content(data_key)
        # return marshal(data, self.schema, envelope='data')
        return marshal(
            {'data': data, 'count': count},
            {'data': fields.Nested(self.schema), 'count': fields.Integer})

    def post(self):
        json_data = request.get_json(force=True)
        valid = False
        for key, obj in json_data.items():
            if key in self.schema:
                valid = True
        if not valid:
            return self.template, hcodes.HTTP_BAD_REQUEST

        # marshal_data = marshal(json_data, self.schema, envelope='data')
        myid = self.insert(json_data)

        # redirect to GET method of this same endpoint, with the id found
        address = url_for(self.table, data_key=myid)
        return redirect(address)


class RethinkConnection(Connection):
    """ Connection for ReThinkDB """

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
        else:
            logger.warning("Using no authentication")

        # Rethinkdb database connection
        try:
            # IMPORTANT! The chosen ORM library does not work if missing repl()
            # at connection time
            self._connection = r.connect(**params).repl()
        except RqlDriverError as e:
            logger.critical("Failed to connect RDB", e)
            return False

        try:
            logger.info("Using database " + APP_DB)
            self._connection.use(APP_DB)
        except RqlDriverError as e:
            logger.critical("Database " + APP_DB + "doesn't exist", e)

        logger.debug("Created Connection")
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


# Need a pool of connections: http://j.mp/1yNP4p0
def try_to_connect():
    if "rdb" in g:
        return False
    try:
        logger.info("Creating the rdb object")
        g.rdb = RethinkConnection()
    except Exception:
        logger.error("Cannot connect")
        return None
        # abort(hcodes.HTTP_INTERNAL_TIMEOUT,
        #     "Problem: no database connection could be established.")
    return True


##########################################
# Read model template
mytemplate = {}
json_autoresources = {}

for fileschema in glob.glob(os.path.join(JSONS_PATH, "*") + "." + JSONS_EXT):
    logger.info("Found RDB schema '%s'" % fileschema)
    # Build current model resource
    with open(fileschema) as f:
        mytemplate = json.load(f)
    reference_schema = convert_to_marshal(mytemplate)

    # Name for the class. Remove path and extension (json)
    label = os.path.splitext(os.path.basename(fileschema))[0].lower()
    # Dynamic attributes
    new_attributes = {
        "schema": reference_schema,
        "template": mytemplate,
        "table": label,
    }
    # Generating the new class
    from ...meta import Meta
    newclass = Meta.metaclassing(RethinkResource, label, new_attributes)
    # Using the same structure i previously used in resources:
    # resources[name] = (new_class, data_model.table)
    json_autoresources[label] = (newclass, label)
