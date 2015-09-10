#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Flask hello world """

from flask import Flask
microservice = Flask(__name__)

@microservice.route("/")
def hello():
    return "Hello World!"
