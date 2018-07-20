# -*- coding: utf-8 -*-

import re

from brck.utils import run_command
from brck.utils import uci_get

from .utils import read_file
from .utils import get_signal_strength

from .schema import Validator

from .sim_utils import connect_sim
from .sim_utils import get_sim_state
from .sim_utils import get_connection_status

from .cache import cached, MINUTE

LOG = __import__('logging').getLogger()

SIM_STATUS_FILES = [
    '/sys/class/gpio/gpio339/value', '/sys/class/gpio/gpio340/value',
    '/sys/class/gpio/gpio341/value'
]

REG_ERROR = re.compile('^.*(ERROR).*$')
REG_PIN_LOCK = re.compile('^.*(PIN).*$')
REG_PUK_LOCK = re.compile('^.*(PUK).*$')
REG_PIN = re.compile(r'^\d{4,8}$')
REG_PUK = re.compile(r'^\d{8}$')
REG_APN = re.compile(r'[\w\.\-]{1,64}')

MOBILE_TECH_MAP = {'0': 'GSM (EDGE)', '2': 'UMTS (3G)', '5': 'LTE (4G)'}


@cached(timeout=(MINUTE * 10), ignore=[{}])
def get_modem_network_info(*args):
    """Gets network information.
    """
    net_info = {}
    try:
        info_str = run_command(
            ['querymodem', 'run', 'AT+XCELLINFO?'], output=True)
        if not info_str:
            info_str = run_command(
                ['querymodem', 'run', 'AT+XCELLINFO?'], output=True)
        LOG.debug("XCELL_INFO INFO: %r", info_str)
        cell_data = info_str.split(',')
        _mode, cell_type, _mcc, mnc, lac, cell_id = cell_data[:6]
        net_info = dict(
            mnc=mnc,
            lac=int('0x{}'.format(lac), 16),
            cell_id=int('0x{}'.format(cell_id), 16),
            net_type=MOBILE_TECH_MAP.get(cell_type, 'Unknown'))
    except Exception as e:
        LOG.error("Failed to load modem network information: %r", e)
    return net_info


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
            conn_paths = [SIM_STATUS_FILES[sim_id_num - 1]]
    net_connected = get_connection_status()
    active_sim = uci_get('brck.active_sim')
    sim_statuses = [read_file(p) for p in conn_paths]
    # when only one SIM is available - assume that's the active SIM
    active_sims = len([s for s in sim_statuses if s == '1'])
    for (i, sim_status) in enumerate(sim_statuses):
        key = i + 1
        c_id = 'SIM%d' % (key)
        name = 'SIM %d' % (key)
        available = False
        connected = False
        if sim_status != False and sim_status == '1':
            available = True
        info = {}
        if available:
            sim_state = get_sim_state(key)
            info['apn_configured'] = sim_state.get('apn', '') != ''
            is_active_sim = (active_sims == 1
                             and net_connected) or (str(key) == active_sim)
            if is_active_sim and (not net_connected):
                sim_status = run_command(
                    ['querymodem', 'check_pin'], output=True) or ''
                if REG_PIN_LOCK.match(sim_status):
                    info['pin_locked'] = True
                else:
                    info['pin_locked'] = False
                if REG_PUK_LOCK.match(sim_status):
                    info['puk_locked'] = True
                else:
                    info['puk_locked'] = False
            elif is_active_sim:
                info['pin_locked'] = False
                info['puk_locked'] = False
                if net_connected:
                    ex_net_info = {}
                    connected = True
                    signal_strength = get_signal_strength('wan')
                    operator = run_command(
                        ['querymodem', 'carrier'], output=True)
                    imei = run_command(['querymodem', 'imei'], output=True)
                    imsi = run_command(['querymodem', 'imsi'], output=True)
                    if REG_ERROR.match(operator) or operator == "0":
                        operator = 'Unknown'
                        connected = False
                    else:
                        ex_net_info['imei'] = imei
                        ex_net_info['imsi'] = imsi
                        ex_net_info['mcc'] = imsi[:3]
                        ex_net_info.update(get_modem_network_info(imsi, imei))
                    ex_net_info.update(
                        dict(
                            operator=operator,
                            signal_strength=signal_strength))
                    info['network_info'] = ex_net_info
        c_data = dict(
            id=c_id,
            name=name,
            available=available,
            connected=connected,
            info=info)
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
        pin = payload.get('pin', '')
        puk = payload.get('puk', '')
        net_config = payload.get('network', {})
        errors = connect_sim(
            sim_id,
            pin=pin,
            puk=puk,
            apn=net_config.get('apn', ''),
            username=net_config.get('username', ''),
            password=net_config.get('password', ''))
        validator.add_errors(errors)
    if validator.is_valid:
        return (200, 'OK')
    else:
        return (422, validator.errors)
