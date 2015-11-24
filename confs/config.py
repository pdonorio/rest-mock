#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
User configuration
"""

import os

#################################
# what you could change
DEBUG = False
STACKTRACE = False
REMOVE_DATA_AT_INIT_TIME = False
SQLLITE_DBFILE = 'latest.db'


###################################################
###################################################
SERVER_HOSTS = '0.0.0.0'
SERVER_PORT = int(os.environ.get('PORT', 5000))

# Other configuration files you may use/need inside the 'confs' directory
LOGGING_CONFIG_FILE = 'logging_config.ini'

# Use this to specifiy endpoints based on your resources module
REST_CONFIG_FILE = 'endpoints.ini'

TRAP_BAD_REQUEST_ERRORS = True
PROPAGATE_EXCEPTIONS = False

# Roles
ROLE_ADMIN = 'adminer'
ROLE_USER = 'justauser'

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

#################################
# SQLALCHEMY
dbfile = os.path.join(BASE_DIR, SQLLITE_DBFILE)
SECRET_KEY = 'my-super-secret-keyword'
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + dbfile
SQLALCHEMY_TRACK_MODIFICATIONS = False

#################################
# SECURITY
ROLE_ADMIN = 'adminer'
ROLE_USER = 'justauser'

# Bug fixing for csrf problem via CURL/token
WTF_CSRF_ENABLED = False
# Force token to last not more than one hour
SECURITY_TOKEN_MAX_AGE = 3600
# Add security to password
# https://pythonhosted.org/Flask-Security/configuration.html
SECURITY_PASSWORD_HASH = "pbkdf2_sha512"
SECURITY_PASSWORD_SALT = "thishastobelongenoughtosayislonglongverylong"
###################################################
###################################################
