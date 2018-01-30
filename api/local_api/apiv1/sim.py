# -*- coding: utf-8 -*-

import re

from brck.utils import run_command
from brck.utils import uci_get
from brck.utils import uci_set
from brck.utils import uci_commit

from utils import read_file
from utils import get_uci_state

from schema import Validator


SIM_STATUS_FILES = [
    '/sys/class/gpio/gpio339/value',
    '/sys/class/gpio/gpio340/value',
    '/sys/class/gpio/gpio341/value'
]

REG_SIM_LOCK = re.compile('^.*(PIN|PUK).*$')
REG_PIN = re.compile('^\d{4}$')
REG_APN = re.compile('[\w\.\-]{1,64}')
REG_OK = re.compile('^.*OK.*$')


def get_wan_connections(sim_id=None):
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
    conn_paths = SIM_STATUS_FILES
    if sim_id is not None:
        sim_id_num = int(sim_id[-1])
        if sim_id_num in [1, 2, 3]:
            conn_paths = SIM_STATUS_FILES[sim_id_num - 1]
    for (i, path) in enumerate(conn_paths):
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


def configure_sim(big_payload):
    """Configures SIM PIN and/or APN.

    Expects payload in this format:

        {
        "configuration": {
            "pin": "1234",
            "network": {
                "apn": "string",
                "username": "string",
                "password": "string"
            }
        }
        }
    :return: (int, list(str))
    """
    payload = big_payload.get('configuration', {})
    m_config = {}
    has_pin = 'pin' in payload
    has_net_config = 'network' in payload
    if has_pin:
        m_config['pin'] = payload['pin']
    if has_net_config:
        m_config.update(payload['network'])
    # validate payloads
    validator = Validator(m_config)
    if has_pin:
        validator.ensure_format('pin', REG_PIN)
    if has_net_config:
        validator.ensure_format('apn', REG_APN)
        validator.required_together('username', 'password')
    if validator.is_valid:
        # Fire off commands
        if has_pin:
            pin = payload['pin']
            r0 = run_command(["querymodem", "set_pin", pin], output=True)
            if REG_OK.match(r0) is None:
                validator.add_error('pin', 'Could not set PIN')
        if validator.is_valid and has_net_config:
            net_config = payload['network']
            uci_set('network.wan.apn', net_config['apn'])
            if net_config.get('username'):
                uci_set('network.wan.username', net_config['username'])
                uci_set('network.wan.password', net_config['password'])
            uci_commit('network.wan')
    if validator.is_valid:
        return (200, 'OK')
    else:
        return (422, validator.errors)