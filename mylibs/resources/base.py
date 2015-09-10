#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Basic Resource """

from flask_restful import Resource

class HelloWorld(Resource):
    def get(self):
        return {'hello': 'world'}

# ####################################
# # Flask normal end-point
# @microservice.route("/foo")
# def hello():
#     return "Hello World!"
