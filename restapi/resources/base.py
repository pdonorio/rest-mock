# -*- coding: utf-8 -*-

""" Basic Resource """

from .. import htmlcodes as hcodes
from confs.config import STACKTRACE
from .. import get_logger
from ..jsonify import output_json, RESTError
from flask.ext.restful import request, Resource, reqparse, fields, abort

logger = get_logger(__name__)


# Extending the concept of rest generic resource
class ExtendedApiResource(Resource):
    """ Implement a generic Resource for Restful model """

    myname = __name__
    _args = {}
    _params = {}
    endtype = None
    endpoint = None
    hcode = hcodes.HTTP_OK_BASIC
    # How to have a standard response
    resource_fields = {
        # html code embedded for semplicity
        'status': fields.Integer,
        # Hashtype, Vector, String, Int/Float, and so on
        'data_type': fields.String,
        # Count
        'elements': fields.Integer,
        # The real data
        'data': fields.Raw,
    }

    def __init__(self):
        super(ExtendedApiResource, self).__init__()
# NOTE: you can add as many representation as you want!
        self.representations = {
            # Be sure of handling JSON
            'application/json': output_json,
        }
        # Apply decision about the url of endpoint
        self.set_endpoint()
        # Make sure you can parse arguments at every call
        self._parser = reqparse.RequestParser()

    @staticmethod
    def clean_parameter(param=""):
        """ I get parameters already with '"' quotes from curl? """
        if param is None:
            return param
        return param.strip('"')

    def parse(self):
        """ Parameters may be necessary at any method """
        self._args = self._parser.parse_args()

    def set_endpoint(self):
        if self.endpoint is None:
            self.endpoint = \
                type(self).__name__.lower().replace("resource", "")

    def get_endpoint(self):
        return (self.endpoint, self.endtype)

    def get_input(self, forcing=True):
        """ Get JSON. The power of having a real object in our hand. """
        return request.get_json(force=forcing)

    def add_parameter(self, name, mytype=str, default=None, required=False):
        """ Save a parameter inside the class """
        self._params[name] = [mytype, default, required]

    def apply_parameters(self):
        """ Use parameters received via decoration """

        ##############################
        # Basic options
        basevalue = str  # Python3
        # basevalue = unicode  #Python2
        act = 'store'  # store is normal, append is a list
        loc = ['headers', 'values']  # multiple locations
        trim = True

        self._params['perpage'] = (int, 10, False)
        self._params['currentpage'] = (int, 1, False)

        for param, (param_type, param_default, param_required) \
          in self._params.items():

            # Decide what is left for this parameter
            if param_type is None:
                param_type = basevalue

            # I am creating an option to handle arrays:
            if param_type == 'makearray':
                param_type = basevalue
                act = 'append'

            # Really add the parameter
            self._parser.add_argument(
                param, type=param_type,
                default=param_default, required=param_required,
                trim=trim, action=act, location=loc)
            logger.debug("Accept param '%s', type %s" % (param, param_type))

    def set_method_id(self, name='myid', idtype='string'):
        """ How to have api/method/:id route possible"""
        self.endtype = idtype + ':' + name

    def response(self, obj=None,
                 elements=0, data_type='dict',
                 fail=False, code=hcodes.HTTP_OK_BASIC):
        """ Handle a standard response following some criteria """

        if fail:
            obj = {'error': obj}
            if code < hcodes.HTTP_BAD_REQUEST:
                code = hcodes.HTTP_BAD_REQUEST

        data_type = str(type(obj))
        if elements < 1:
            if isinstance(obj, str):
                elements = 1
            else:
                elements = len(obj)

        response = {
            'data': obj,
            'elements': elements,
            'data_type': data_type,
            'status': code
        }

        # ## In case we want to handle the failure at this level
        # # I want to use the same marshal also if i say "fail"
        # if fail:
        #     code = hcodes.HTTP_BAD_REQUEST
        #     if STACKTRACE:
        #         # I could raise my exception if i need again stacktrace
        #         raise RESTError(obj, status_code=code)
        #     else:
        #         # Normal abort
        #         abort(code, **response)
        # ## But it's probably a better idea to do it inside the decorators

        return response, code
