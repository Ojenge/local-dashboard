# -*- coding: utf-8 -*-

"""
API Controllers for the local dashboard
"""

from flask import Blueprint, jsonify, request, abort
from flask.views import MethodView

from utils import get_system_state
from utils import configure_system

api_blueprint = Blueprint('apiv1', __name__)


GET = 'GET'
POST = 'POST'
PATCH = 'PATCH'
HTTP_OK = 200


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
        status, response = configure_system(payload)
        if status == HTTP_OK:
            return jsonify(get_system_state())
        else:
            abort(jsonify(response), status)

api_blueprint.add_url_rule('/system',
                           view_func=SystemAPI.as_view('system_api'),
                           methods=[GET, PATCH])