# -*- coding: utf-8 -*-

"""
Define how your APIs
should get Requests objects
or set Responses objects
based on JSON formats
"""

from flask_restful import fields


##########################################
# ## Marshal
# http://flask-restful-cn.readthedocs.org/en/0.3.4/api.html#module-fields
def marshal_type(obj):
    mytype = fields.Raw
    if isinstance(obj, str):  # or isinstance(obj, unicode):
        if obj == 'NativeTime':
            mytype = fields.DateTime(dt_format='rfc822')
        else:
            mytype = fields.String
    elif isinstance(obj, int):
        mytype = fields.Integer
    return mytype


# // TO FIX:
# should be recursive for nested structures
def convert_to_marshal(data):
    mymarshal = {}
    # Case of dict
    for key, obj in data.items():
        mymarshal[key] = marshal_type(obj)
    # Case of lists?

    #print("MARSHAL!", mymarshal)
    return mymarshal
