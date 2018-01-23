# -*- coding: utf-8 -*-

"""
API Controllers for the local dashboard
"""

from flask import Blueprint, jsonify, request, abort, make_response
from flask.views import MethodView

from utils import get_system_state
from utils import configure_system

api_blueprint = Blueprint('apiv1', __name__)


GET = 'GET'
POST = 'POST'
PATCH = 'PATCH'
HTTP_OK = 200


class APIErrorData(Exception):
    

    def __init__(self, message='Error', payload={}, status_code=400):
        Exception.__init__(self)
        self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        r = {}
        r['message'] = self.message
        r['errors'] = self.payload
        return r


@api_blueprint.app_errorhandler(APIErrorData)
def handle_bad_data_error(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


class Ping(MethodView):
    
    def get(self):
        """Provides a PING API
        """
        return jsonify(dict(about='SupaBRCK Local Dashboard',
                            version='0.1'))


class SystemAPI(MethodView):

    def get(self):
        """Returns a JSON struct of the system API

            See System API documentation

        :return: string JSON representation of system state
        """
        state = get_system_state()
        return jsonify(state)

    def patch(self):
        """Provides an API to perform system changes

            See System API documentation (Configuring the system)
        
        :return: string JSON representation of new system state or error
        """
        payload = request.get_json()
        status_code, errors = configure_system(payload)
        if status_code == HTTP_OK:
            return jsonify(get_system_state())
        else:
            raise APIErrorData('Invalid Data', errors, 422)

api_blueprint.add_url_rule('/ping',
                           view_func=Ping.as_view('ping'),
                           methods=[GET])
api_blueprint.add_url_rule('/system',
                           view_func=SystemAPI.as_view('system_api'),
                           methods=[GET, PATCH])