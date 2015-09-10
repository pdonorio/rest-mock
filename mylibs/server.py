#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Flask hello world """

####################################
# Create app
from flask import Flask
microservice = Flask(__name__)
# and then add every other needed part

"""
# // TO FIX: find logging best practice
# ####################################

# # Logging format?

# # Logging to file ?
# import logging
# from logging.handlers import RotatingFileHandler
# handler = RotatingFileHandler('foo.log', maxBytes=10000, backupCount=1)
# handler.setLevel(logging.INFO)
# microservice.logger.addHandler(handler)

# // TO FIX: missing package
# ####################################
# # Allow cross-domain requests for JS and Upload
# from flask.ext.cors import CORS
# CORS(app, headers=['Content-Type'])
"""

####################################
# RESTful Resources

# // TO FIX: list via python objects introspection
resources = []
from mylibs.resources.base import HelloWorld
resources.append((HelloWorld, 'foo'))

# do it
from mylibs.resources import create_endpoints
create_endpoints(resources, microservice)
