#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
First base: RESTful API python3 flask server
"""

from mylibs.server import microservice as app
from confs.config import SERVER_HOSTS, SERVER_PORT, DEBUG

if __name__ == "__main__":
    app.run(host=SERVER_HOSTS, port=SERVER_PORT, debug=DEBUG)
