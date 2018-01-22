# -*- coding: utf-8 -*-

"""
API Controllers for the local dashboard
"""

from flask import Blueprint, jsonify
from flask.views import MethodView

from utils import get_storage_status
from utils import get_battery_status
from utils import get_device_mode
from utils import get_network_status
from utils import get_power_config

api_blueprint = Blueprint('apiv1', __name__)


GET = 'GET'
POST = 'POST'
PATCH = 'PATCH'


class SystemAPI(MethodView):

    def get(self):
        """Returns a JSON struct of the system API

            Example Response:
            ```
                    {
                    "id": "string",
                    "battery": {
                        "state": "CHARGING",
                        "battery_level": 0
                    },
                    "storage": {
                        "available_space": 0,
                        "used_space": 0,
                        "total_space": 0
                    },
                    "mode": "MATATU",
                    "power": {
                        "soc_on": 0,
                        "soc_off": 0,
                        "turn_on_time": "00:00",
                        "turn_off_time": "00:00"
                    },
                    "network": {
                        "connected": true,
                        "connection": {
                        "connection_type": "WAN",
                        "up_speed": 1000000,
                        "down_speed": 1000000,
                        "signal_strengh": 77
                        },
                        "connected_clients": 0
                    }
                    }
            ```

        :return: string
        """
        mode = get_device_mode()
        storage_state = get_storage_status()
        battery_state = get_battery_status()
        power_state = get_power_config()
        network_state = get_network_status()
        state = dict(
            mode=mode,
            storage=storage_state,
            battery=battery_state,
            power=power_state,
            network=network_state
        )
        return jsonify(state)



system_view = SystemAPI.as_view('system_api')
api_blueprint.add_url_rule('/system',
                           view_func=system_view,
                           methods=[GET, PATCH])