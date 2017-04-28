# -*- coding: utf-8 -*-

import gspread
from oauth2client.service_account import ServiceAccountCredentials
from restapi.resources.services.elastic import EL_INDEX3, EL_TYPE1
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

LEXIQUE_TABLE = 'lexique'
ENCODING = 'utf-8'
keys = ['sheet', 'macro', 'micro', 'titre', 'latin', 'italien', 'français']


class GExReader(object):
    """ Reading google spreadsheets online """

    def __init__(self, filename=None, rethink=None, elastic=None):

        if filename is None:
            filename = "/uploads/data/test2.xlsx"

        if rethink is not None:
            q = rethink.get_query()
            # drop table if exist
            if LEXIQUE_TABLE in q.table_list().run():
                q.table_drop(LEXIQUE_TABLE).run()
            # create table
            q.table_create(LEXIQUE_TABLE, primary_key='titre').run()
            # set index as convention/titre

            # save the main object
            self._r = rethink.get_table_query(LEXIQUE_TABLE)
        else:
            self._r = None

        if elastic is not None:
            self._el = elastic
        else:
            self._el = None

        # CONNECT
        filename = 'Voc typol_CH_Rd'
        fileconf = './confs/endpoints/gxls_client.json'

        # use creds to create a client to interact with the Google Drive API
        scope = ['https://spreadsheets.google.com/feeds']
        creds = ServiceAccountCredentials \
            .from_json_keyfile_name(fileconf, scope)
        client = gspread.authorize(creds)
        self._xls = client.open(filename)

    def get_data(self):

        print("Getting data")
        sheet = self._xls.sheet1

        for row_num in range(2, sheet.row_count):

            print("ROW", row_num - 1)
            row = sheet.row_values(row_num)

            term = {}
            empty = True
            for cell_num in range(0, len(keys)):
                value = row[cell_num].strip()
                if value != '':
                    empty = False
                # value = value.encode(ENCODING)
                # key = keys[cell_num].encode(ENCODING)
                key = keys[cell_num]
                # print(key, value)
                term[key] = value

            if empty:
                return False

            ######################
            # SAVE

            # Save rethinkdb
            self._r.insert(term).run()
            # Update elastic specific index
            self._el.index(
                index=EL_INDEX3, id=row_num, body=term, doc_type=EL_TYPE1)

            # print(term)
            # return False

        return True
        # print(list_of_hashes)
