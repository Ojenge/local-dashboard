# -*- coding: utf-8 -*-

"""
API Controllers for the local dashboard
"""

import re

from flask import Blueprint, jsonify, request
from flask.views import MethodView

from flask_login import (
    login_required,
    current_user
)
from .errors import APIError
from .utils import (
    get_system_state,
    get_battery_status,
    get_software,
    get_diagnostics_data,
    get_device_mode,
    get_device_setup_data,
    get_connection_state,
    get_retail_registration_token,
    retail_device_registered,
    get_device_id
)
from .sim import (
    get_wan_connections,
    configure_sim
)
from .ethernet import (
    get_ethernet_networks,
    configure_ethernet
)
from .wifi import (
    get_wireless_config,
    configure_wifi
)
from .soc import (
    configure_power,
    get_power_config
)
from .models import (
    check_password,
    make_token,
    change_password
)

api_blueprint = Blueprint('apiv1', __name__)


GET = 'GET'
POST = 'POST'
PATCH = 'PATCH'
POST = 'POST'
HTTP_OK = 200

# Route regexes
SIM_ID_REGEX = re.compile(r'^SIM[1-3]$')
ETHERNET_ID_REGEX = re.compile(r'^ETHERNET[1-3]$')
WIFI_ID_REGEX = re.compile(r'^WIFI[1]$')


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


class ChangePasswordView(ProtectedView):
    
    def patch(self):
        """Sets a new user password
        :return: string json
        """
        payload = request.get_json() or {}
        status_code, errors = change_password(payload, current_user.login)
        if status_code == HTTP_OK:
            return jsonify({})
        else:
            raise APIError('Invalid Data', errors, 422)


class DeviceModeAPI(MethodView):
    def get(self):
        """Returns the mode the device is in
        """
        mode = get_device_mode()
        login_id, mac_id = get_device_setup_data()
        device_id = get_device_id()
        setup_link = "https://my.brck.com/devices/%s/" % device_id
        if mode == "RETAIL":
            if not retail_device_registered():
                registration_token = get_retail_registration_token()
                setup_link = "https://my.brck.com/setup/%s/%s/" % (
                    login_id,
                    registration_token)
        connected = get_connection_state()
        return jsonify({"mode": mode, "setup_link": setup_link,
                        "connected": connected})


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


class PowerAPI(ProtectedView):
    
    def get_config(self, **kwargs):
        if 'live' in request.args:
            kwargs['no_cache'] = True
        config = get_power_config(**kwargs)
        battery = get_battery_status(**kwargs)
        config['battery'] = battery
        return config

    def get(self):
        """Returns the current power configuration of the device

        :return: string JSON representation of system state
        """
        return jsonify(self.get_config())
    
    def patch(self):
        """Provides an API to perform system power changes

            See System API documentation (Configuring the system)
        
        :return: string JSON representation of new system state or error
        """
        payload = request.get_json() or {}
        power_config = payload.get('power') or {}
        status_code, errors = configure_power(power_config)
        if status_code == HTTP_OK:
            return jsonify(self.get_config(no_cache=True))
        else:
            raise APIError('Invalid Data', errors, 422)

class SoftwareAPI(ProtectedView):
    
    def get(self):
        """Gets the current software state of the device (os, firmware, packages)

        :return: JSON representation of software version.
        """
        return jsonify(get_software())


class DiagnosticsAPI(ProtectedView):
    
    def get(self):
        """Gets diagnostics info for a SupaBRCK

        Includes:

        - battery temperature
        - device temperature
        - modem temperature
        - connected clients

        Raw information may also be downloaded.
        """
        return jsonify(get_diagnostics_data())


class WANAPI(ProtectedView):

    def check_sim_id(self, sim_id):
        if sim_id is None or SIM_ID_REGEX.match(sim_id) is None:
            raise APIError(message='Not Found', status_code=404)

    def get(self, sim_id):
        """Returns a list of availalable WAN connections.

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


class EthernetAPI(ProtectedView):
    
    def check_net_id(self, net_id):
        if net_id is None or ETHERNET_ID_REGEX.match(net_id) is None:
            raise APIError(message='Not found', status_code=404)
    
    def get(self, net_id):
        """Returns list of available ethernet connections.

            See the API docs for sample responses.

        :return: string (JSON list of connection information)
        """
        if net_id is None:
            connections = get_ethernet_networks()
            return jsonify(connections)
        else:
            self.check_net_id(net_id)
            connection = get_ethernet_networks(net_id=net_id)[0]
            return jsonify(connection)
    
    def patch(self, net_id):
        self.check_net_id(net_id)
        payload = request.get_json()
        if payload is None:
            raise APIError('Invalid Data', [], 422)
        status_code, errors = configure_ethernet(net_id, payload)
        if status_code == HTTP_OK:
            return jsonify(get_ethernet_networks(net_id)[0])
        else:
            raise APIError('Invalid Data', errors, 422)


class WIFIAPI(ProtectedView):
    
    def check_net_id(self, net_id):
        if net_id is None or WIFI_ID_REGEX.match(net_id) is None:
            raise APIError(message='Not found', status_code=404)
    
    def get(self, net_id):
        """Returns list of available wifi connections.

            See the API docs for sample responses.

        :return: string (JSON list of connection information)
        """
        if net_id is None:
            connections = get_wireless_config()
            return jsonify(connections)
        else:
            self.check_net_id(net_id)
            connection = get_wireless_config(net_id)[0]
            return jsonify(connection)


    def patch(self, net_id):
        self.check_net_id(net_id)
        payload = request.get_json()
        if payload is None:
            raise APIError('Invalid Data', [], 422)
        status_code, errors = configure_wifi(net_id, payload)
        if status_code == HTTP_OK:
            return jsonify(get_wireless_config(net_id)[0])
        else:
            raise APIError('Invalid Data', errors, 422)



api_blueprint.add_url_rule('/auth',
                           view_func=AuthenticationView.as_view('auth'),
                           methods=[POST])
api_blueprint.add_url_rule('/auth/password',
                           view_func=ChangePasswordView.as_view('change_password'),
                           methods=[PATCH])
sim_view = WANAPI.as_view('sim_api')
api_blueprint.add_url_rule('/networks/sim/',
                           defaults={'sim_id': None},
                           view_func=sim_view,
                           methods=[GET])
api_blueprint.add_url_rule('/networks/sim/<string(length=4):sim_id>',
                           view_func=sim_view,
                           methods=[GET, PATCH])
eth_view = EthernetAPI.as_view('ethernet_api')
api_blueprint.add_url_rule('/networks/ethernet/',
                           defaults={'net_id': None},
                           view_func=eth_view,
                           methods=[GET])
api_blueprint.add_url_rule('/networks/ethernet/<string(length=9):net_id>',
                           view_func=eth_view,
                           methods=[GET, PATCH])
wifi_view = WIFIAPI.as_view('wif_api')
api_blueprint.add_url_rule('/networks/wifi/',
                           defaults={'net_id': None},
                           view_func=wifi_view,
                           methods=[GET])
api_blueprint.add_url_rule('/networks/wifi/<string(length=5):net_id>',
                           view_func=wifi_view,
                           methods=[GET, PATCH])
api_blueprint.add_url_rule('/ping',
                           view_func=Ping.as_view('ping'),
                           methods=[GET])
api_blueprint.add_url_rule('/system',
                           view_func=SystemAPI.as_view('system_api'),
                           methods=[GET, PATCH])
api_blueprint.add_url_rule('/system/software',
                           view_func=SoftwareAPI.as_view('software_api'),
                           methods=[GET])
api_blueprint.add_url_rule('/system/diagnostics',
                           view_func=DiagnosticsAPI.as_view('diagnostics_api'),
                           methods=[GET])
api_blueprint.add_url_rule('/power',
                           view_func=PowerAPI.as_view('power_api'),
                           methods=[GET, PATCH])
api_blueprint.add_url_rule('/device-mode',
                           view_func=DeviceModeAPI.as_view('device_mode_api'),
                           methods=[GET])
