# -*- coding: utf-8 -*-

"""
API Controllers for the local dashboard
"""

from flask import Blueprint, jsonify, request, abort, make_response
from flask.views import MethodView

from flask_login import login_required

from utils import get_system_state
from utils import configure_system
from errors import APIError
from sim import get_wan_connections

api_blueprint = Blueprint('apiv1', __name__)


GET = 'GET'
POST = 'POST'
PATCH = 'PATCH'
HTTP_OK = 200


@api_blueprint.app_errorhandler(APIError)
def handle_bad_data_error(error):
    """API Error handler
    :return: flask.Response
    """
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


class Ping(MethodView):
    
    decorators = [login_required]

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
            raise APIError('Invalid Data', errors, 422)


class WANAPI(MethodView):
    
    def get(self):
        """Returns a list of active WAN connections.

        This depends on the number of SIM slots available on the SupaBRCK.
        
        :return: string JSON list of WAN connections on device. 
        """
        connections = get_wan_connections()
        return jsonify(connections)


api_blueprint.add_url_rule('/networks/sim',
                           view_func=WANAPI.as_view('sim'),
                           methods=[GET])
api_blueprint.add_url_rule('/ping',
                           view_func=Ping.as_view('ping'),
                           methods=[GET])
api_blueprint.add_url_rule('/system',
                           view_func=SystemAPI.as_view('system_api'),
                           methods=[GET, PATCH])