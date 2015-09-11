#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Flask hello world """

####################################
# Create app
from flask import Flask
microservice = Flask(__name__)
# and then add every other needed part

# // TO FIX: missing package
# ####################################
# # Allow cross-domain requests for JS and Upload
# from flask.ext.cors import CORS
# CORS(app, headers=['Content-Type'])

####################################
# RESTful automatic Resources

from mylibs.resources import create_endpoints, mock as mymodule
create_endpoints(mymodule, microservice)
