#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Configuration handler """

import configparser
import logging
from mylibs import REST_CONFIG
from mylibs.meta import Meta

logger = logging.getLogger(__name__)

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

                # Meta language for dinamically import
                try:
                    myclass = getattr(module, classname)
                    logger.debug("Found " + section + '.' + classname)
                except AttributeError as e:
                    logger.critical("Failed to load resource: " + str(e))
                    continue

                # Get the best endpoint comparing inside against configuration
                instance = myclass()
                oldendpoint, endkey = instance.get_endpoint()
                if endpoint.strip() == '':
                    endpoint = oldendpoint

                resources.append((myclass, instance, endpoint, endkey))

                # # Load
                # create_endpoint(rest_api, myclass, endpoint, endkey)

        return resources