#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Configuration handler """

from __future__ import absolute_import
import glob
import os
from jinja2._compat import iteritems
from . import get_logger, REST_CONFIG
from .meta import Meta
try:
    import configparser
except:
    # python2
    import ConfigParser as configparser

logger = get_logger(__name__)


class MyConfigs(object):
    """ A class to read all of my configurations """

    _latest_config = None

    def read_config(self, configfile, case_sensitive=True):
        """ A generic reader via standard library """

        if case_sensitive:
            # Make sure configuration is case sensitive
            config = configparser.RawConfigParser()
            config.optionxform = str
        else:
            config = configparser.ConfigParser()

        # Read
        config.read(configfile)
        self._latest_config = config
        return config

    def single_rest(self, ini_file):

        meta = Meta()
        resources = []
        config = self.read_config(ini_file)

        for section in config.sections():

            logger.info("Configuration read: {Section: " + section + "}")

            module = meta.get_module_from_string(
                __package__ + '.resources.' + section)
            # Skip what you cannot use
            if module is None:
                logger.warning("Could not find module '%s'..." % section)
                continue

            for classname, endpoint in iteritems(dict(config.items(section))):

                myclass = meta.get_class_from_string(classname, module)
                # Again skip
                if myclass is None:
                    continue
                else:
                    logger.debug("REST! Found resource: " +
                                 section + '.' + classname)

                # Get the best endpoint comparing inside against configuration
                instance = myclass()
                oldendpoint, endkey = instance.get_endpoint()
                if endpoint.strip() == '':
                    endpoint = oldendpoint

                resources.append((myclass, instance, endpoint, endkey))

        return resources

    def rest(self):
        """ REST endpoints from '.ini' files """

        resources = []
        logger.debug("Trying configurations from '%s' dir" % REST_CONFIG)

# TO CHANGE:
# READ ONLY INI FILE FROM THE JSON CONFIG

        for ini_file in glob.glob(os.path.join(REST_CONFIG, "*") + ".ini"):
            logger.info("REST configuration file '%s'" % ini_file)
            # Add all resources from this single ini file
            resources.extend(self.single_rest(ini_file))

        return resources
