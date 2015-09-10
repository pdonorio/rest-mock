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
# RESTful
from flask_restful import Resource, Api
rest_api = Api(microservice, catch_all_404s=True)

####################################
# Uploader Resource
FIXED_APIURL = '/api' + '/'
resources = []

class HelloWorld(Resource):
    def get(self):
        return {'hello': 'world'}

resources.append((HelloWorld, 'foo'))

for resource, endpoint in resources:
# // TO FIX: endpoint from the class?
    # endpoint, endkey = resource().get_endpoint()
    print(resource, endpoint)

    # Create restful endpoint
    rest_api.add_resource(resource, FIXED_APIURL+endpoint)
#        ,\ FIXED_APIURL + endpoint +'/<'+ endkey +'>')

# ####################################
# # Flask normal end-points
# @microservice.route("/foo")
# def hello():
#     return "Hello World!"
