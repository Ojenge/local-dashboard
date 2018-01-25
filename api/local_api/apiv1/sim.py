# -*- coding: utf-8 -*-

import re

from brck.utils import run_command

from utils import read_file
from utils import get_uci_state


SIM_STATUS_FILES = [
    '/sys/class/gpio/gpio339/value',
    '/sys/class/gpio/gpio340/value',
    '/sys/class/gpio/gpio341/value'
]

REG_SIM_LOCK = re.compile('^.*(PIN|PUK).*$')


def get_wan_connections():
    """Returns list of SIM connections

    Sample Reponse:

        [
        {
            "id": "SIM1",
            "name": "SIM 1",
            "connection_type": "SIM",
            "connection_available": true,
            "connected": true,
            "info": {
                "sim_locked": true,
                "apn_configured": true,
                "network_info": {
                    "operator": "Operator Name",
                    "imei": 350089999084990,
                    "cell_id": 300300,
                    "lac": 300,
                    "mnc": 304,
                    "mcc": 639,
                    "network_type": "2G"
                }
            }
        }
        ]

    :return: list(dict)
    """
    conns = []
    for (i, path) in enumerate(SIM_STATUS_FILES):
        key = i + 1
        c_id = 'SIM%d' %(key)
        name = 'SIM %d' % (key)
        file_resp = read_file(path)
        available = False
        connected = False
        if file_resp != False and file_resp == '1':
            available = True
        info = {}
        if available:
            uci_state = get_uci_state('network.wan')
            connected = uci_state.get('network.wan.connected', '') == '1'
            info['apn_configured'] = bool(uci_state.get('network.wan.apn'))
            if not connected:
                sim_status = run_command(['querymodem', 'check_pin'],
                                         output=True)
                if REG_SIM_LOCK.match(sim_status):
                    info['sim_locked'] = True
                else:
                    info['sim_locked'] = False
            else:
                 info['sim_locked'] = False
        c_data = dict(
            id=c_id,
            name=name,
            available=available,
            connected=connected,
            info=info
        )
        conns.append(c_data)
    return conns
