# -*- coding: utf-8 -*-

import re

from brck.utils import run_command
from brck.utils import uci_get
from brck.utils import uci_set
from brck.utils import uci_commit

from .utils import read_file
from .utils import get_uci_state

from .schema import Validator

from .sim_utils import connect_sim

SIM_STATUS_FILES = [
    '/sys/class/gpio/gpio339/value',
    '/sys/class/gpio/gpio340/value',
    '/sys/class/gpio/gpio341/value'
]

REG_PIN_LOCK = re.compile('^.*(PIN).*$')
REG_PUK_LOCK = re.compile('^.*(PUK).*$')
REG_PIN = re.compile('^\d{4,8}$')
REG_PUK = re.compile('^\d{8}$')
REG_APN = re.compile('[\w\.\-]{1,64}')


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
                "pin_locked": true,
                "puk_locked": false,
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
                if REG_PIN_LOCK.match(sim_status):
                    info['pin_locked'] = True
                else:
                    info['pin_locked'] = False
                if REG_PUK_LOCK.match(sim_status):
                    info['puk_locked'] = True
                else:
                    info['puk_locked'] = False
            else:
                 info['pin_locked'] = False
                 info['puk_locked'] = False
        c_data = dict(
            id=c_id,
            name=name,
            available=available,
            connected=connected,
            info=info
        )
        conns.append(c_data)
    return conns


def configure_sim(sim_id, big_payload):
    """Configures SIM PIN and/or APN.

    Expects payload in this format:

        {
        "configuration": {
            "pin": "1234",
            "puk": "12345678",
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
    has_puk = 'puk' in payload
    has_net_config = 'network' in payload
    if has_pin:
        m_config['pin'] = payload['pin']
    if has_puk:
        m_config['puk'] = payload['puk']
    if has_net_config:
        m_config.update(payload['network'])
    # validate payloads
    validator = Validator(m_config)
    if has_pin:
        validator.ensure_format('pin', REG_PIN)
    if has_puk:
        validator.ensure_format('puk', REG_PUK)
        validator.required_together('pin', 'puk')
    if has_net_config:
        validator.ensure_format('apn', REG_APN)
        validator.required_together('username', 'password')
    if validator.is_valid:
        # Fire off commands
        if validator.is_valid and has_net_config:
            net_config = payload['network']
            uci_set('network.wan.apn', net_config['apn'])
            if net_config.get('username'):
                uci_set('network.wan.username', net_config['username'])
                uci_set('network.wan.password', net_config['password'])
            uci_commit('network.wan')
        if validator.is_valid:
            pin = payload.get('pin', '')
            puk = payload.get('puk', '')
            errors = connect_sim(sim_id, pin, puk)
            validator.add_errors(errors)
    if validator.is_valid:
        return (200, 'OK')
    else:
        return (422, validator.errors)