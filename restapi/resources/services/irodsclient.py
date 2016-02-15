# -*- coding: utf-8 -*-

""" iRODS abstraction for FS virtualization with resources """

from restapi import get_logger
from plumbum import local

logger = get_logger(__name__)


#####################################
# IRODS CLASS
class MyRods(object):
    """ A class to use irods through icommands """
# GET EVERYTHING FROM irods2graph

    def other(self):

        try:
            out = local['ils']()
            logger.info("Work in progress", out)
        except Exception as e:
            logger.warning("Irods failed with '%s'" % str(e))

        return True

mirods = MyRods()
