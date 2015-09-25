#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Configuration handler """

from mylibs import get_logger
logger = get_logger(__name__)

import configparser
from mylibs import REST_CONFIG
from mylibs.meta import Meta

class MyConfigs(object):
    """ A class to read all of my configurations """

    _latest_config = None

    def read_config(self, configfile, case_sensitive=True):
        """ A generic reader via standard library """

        if case_sensitive:
            # Make sure configuration is case sensitive
            config = configparser.RawConfigParser()
            config.optionxform = str
        else:
            config = configparser.ConfigParser()

        # read ?
        config.read(configfile)
        self._latest_config = config
        return config

    def rest(self):

        config = self.read_config(REST_CONFIG)
        sections = config.sections()
        logger.debug("Trying configuration from " + REST_CONFIG)

        meta = Meta()

        resources = []

        for section in sections:
            logger.debug("Section " + section)

            module = meta.get_module_from_string('mylibs.resources.' + section)
            # Skip what you cannot use
            if module is None:
                continue

            for classname, endpoint in config[section].items():

                myclass = meta.get_class_from_string(classname, module)
                # Skip what you cannot use
                if myclass is None:
                    continue
                else:
                    logger.debug("Found " + section + '.' + classname)

                # Get the best endpoint comparing inside against configuration
                instance = myclass()
                oldendpoint, endkey = instance.get_endpoint()
                if endpoint.strip() == '':
                    endpoint = oldendpoint

                resources.append((myclass, instance, endpoint, endkey))

        return resources