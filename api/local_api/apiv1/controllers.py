# -*- coding: utf-8 -*-

"""
API Controllers for the local dashboard
"""

import re

from flask import Blueprint, jsonify, request
from flask.views import MethodView

from flask_login import login_required

from .utils import get_system_state
from .errors import APIError
from .sim import get_wan_connections
from .sim import configure_sim
from .soc import configure_power
from .models import check_password
from .models import make_token

api_blueprint = Blueprint('apiv1', __name__)


GET = 'GET'
POST = 'POST'
PATCH = 'PATCH'
POST = 'POST'
HTTP_OK = 200

# Route regexes
SIM_ID_REGEX = re.compile('^(SIM1|SIM2|SIM3)$')


@api_blueprint.app_errorhandler(APIError)
def handle_bad_data_error(error):
    """API Error handler
    :return: flask.Response
    """
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


class AuthenticationView(MethodView):
    """Authentication views.
    """

    def post(self):
        """Responds with an authorized token or error.
        :return:
        """
        payload = request.get_json()
        login = payload.get('login')
        password = payload.get('password')
        if check_password(login, password):
            return jsonify(make_token(login))
        else:
            raise APIError(message='Bad Credentials', status_code=401)


class Ping(MethodView):
    
    def get(self):
        """Provides a PING API
        """
        return jsonify(dict(about='SupaBRCK Local Dashboard',
                            version='0.1'))


class ProtectedView(MethodView):
    """Protected view requiring authorization
    """

    decorators = [login_required]


class SystemAPI(ProtectedView):

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
        payload = request.get_json() or {}
        power_config = payload.get('power') or {}
        status_code, errors = configure_power(power_config)
        if status_code == HTTP_OK:
            return jsonify({})
        else:
            raise APIError('Invalid Data', errors, 422)


class WANAPI(ProtectedView):

    def check_sim_id(self, sim_id):
        if sim_id is None or SIM_ID_REGEX.match(sim_id) is None:
            raise APIError(message='Not Found', status_code=404)

    def get(self, sim_id):
        """Returns a list of active WAN connections.

        This depends on the number of SIM slots available on the SupaBRCK.
        
        :return: string JSON list of WAN connections on device or a single record.
        """
        if sim_id is None:
            connections = get_wan_connections()
            return jsonify(connections)
        else:
            self.check_sim_id(sim_id)
            connection = get_wan_connections(sim_id)[0]
            return jsonify(connection)

    def patch(self, sim_id):
        self.check_sim_id(sim_id)
        payload = request.get_json()
        if payload is None:
            raise APIError("Invalid Data", [], 422)
        status_code, errors = configure_sim(sim_id, payload)
        if status_code == HTTP_OK:
            return jsonify(get_wan_connections(sim_id))
        else:
            raise APIError("Invalid Data", errors, 422)

api_blueprint.add_url_rule('/auth',
                           view_func=AuthenticationView.as_view('auth'),
                           methods=[POST])
sim_view = WANAPI.as_view('user_api')
api_blueprint.add_url_rule('/networks/sim/',
                           defaults={'sim_id': None},
                           view_func=sim_view,
                           methods=[GET])
api_blueprint.add_url_rule('/networks/sim/<string(length=4):sim_id>',
                           view_func=sim_view,
                           methods=[GET, PATCH])
api_blueprint.add_url_rule('/ping',
                           view_func=Ping.as_view('ping'),
                           methods=[GET])
api_blueprint.add_url_rule('/system',
                           view_func=SystemAPI.as_view('system_api'),
                           methods=[GET, PATCH])