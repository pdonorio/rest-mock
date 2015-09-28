#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
First base: RESTful API python3 flask server
"""

from mylibs.server import microservice as app

options = {
    # Open the server to requests from outside the host
    'host': "0.0.0.0",
    #'port': 8080,
    #'debug': True,
}

if __name__ == "__main__":
    app.run(**options)
