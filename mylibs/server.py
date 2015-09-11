#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Flask hello world """

####################################
# Create app
from flask import Flask
microservice = Flask(__name__)
# and then add every other needed part

####################################
# Allow cross-domain requests
# e.g. for JS and Upload
from flask_cors import CORS
CORS(microservice, headers=['Content-Type'])

####################################
# RESTful automatic Resources
from mylibs.resources import create_endpoints, mock as mymodule
create_endpoints(mymodule, microservice)
