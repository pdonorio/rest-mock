# -*- coding: utf-8 -*-

""" Client for api """

import requests

NODE = 'api'
PORT = 5000
USER = 'user@nomail.org'
PW = 'test'

URL = 'http://%s:%s' % (NODE, PORT)
LOGIN_URL = URL + '/login'
HEADERS = {'user-agent': 'my-app/0.0.1'}

r = requests.post(LOGIN_URL, headers=HEADERS, auth=(USER, PW))
# payload = {USER: PW}
# r = requests.post(URL + '/login', params=payload)

###################
print(r, r.url)
print("RESPONSE:")
try:
    print(r.json())
except:
    print(r.text)
