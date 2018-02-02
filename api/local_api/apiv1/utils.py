# -*- coding: utf-8 -*-

"""
Utilities for interacting with the filesystem.
"""

import os
import re
import time

from brck.utils import run_command
from brck.utils import uci_get
from brck.utils import uci_set
from brck.utils import uci_commit

from .schema import Validator
from .soc import get_soc_settings


LOG = __import__('logging').getLogger()

STATE_OK = 'OK'
STATE_ERROR = 'ERROR'
STATE_UNKNOWN = 'UNKNOWN'
DEVICE_MODES = ['MATATU', 'ALWAYS_ON', 'RETAIL', 'SOLAR_POWERED']

REGEX_TIME = re.compile('^(0[0-9]|1[0-9]|2[0-3]):(0[0-9]|[1-5][0-9])$')


def get_request_log(r):
    """Gets request metadata as a string for logging

    Includes: user agent, remote address, path

    :return: string
    """
    return "%s|%s|%s" % (r.remote_addr, r.path, r.user_agent)



def get_uci_state(option, command='show', as_dict=True):
    """Gets the uci state stored at `option`

    :param str option: the name of the uci option
    :param str command: the command to run on state (`show` or `get`)
    :param bool expand_options: whether the response should be expanded
    :return: dict|string
    """
    cmd_list = ['uci', '-P']
    cmd_list.append('/var/state')

    cmd_list.append(command)
    cmd_list.append(option)

    response = run_command(cmd_list, output=True)
    out = response
    if as_dict:
        out = dict()
        if not(response is False) and len(response):
            out.update([l.replace("'", "").split('=') for l in response.splitlines()])
    return out


def get_signal_strength(net_type):
    """Get wireless signal strength (Mobile)

    :return: int (percentage 0-100)
    """
    if net_type == 'wan':
        signal_strength = 0
        resp = run_command(['querymodem', 'signal'], output=True)
        try:
            rssi = int(resp or '')
            if (rssi >= 0 and rssi <= 31):
                signal_strength = (rssi * 827 + 127) >> 8
        except ValueError:
            LOG.error("Failed to load signal strength: QueryModem Response: %s", resp)
    else:
        signal_strength = 100
    return signal_strength


def read_file(path):
    """Reads the file contents at `path`

    :param str path: the the path to read
    :return: str contents of the file or False if file reading failed
    """
    contents = False
    try:
        with open(path) as f:
            contents = f.read().strip()
    except IOError:
        LOG.error('Failed to read file at %s', path)
    return contents


def get_device_mode():
    """Returns the device mode

    May be one of

    - MATATU
    - ALWAYS_ON
    - RETAIL
    - SOLAR_POWERED
    - UNKNOWN

    :return: str
    """
    resp = uci_get('brck.soc.mode')
    mode = STATE_UNKNOWN
    if resp and len(mode):
        return mode
    return mode


def get_storage_status(mount_point='/storage/data'):
    """Gets the disk storage status of a BRCK device in bytes.

    The default mountpoint `/storage/data`.

    Assumes that everything is mounted under /
    :return: dict
    """
    state = dict(
        total_space=0,
        used_space=0,
        available_space=0
    )
    try:
        stats = os.statvfs(mount_point)
        state = dict(
            total_space=stats.f_blocks * stats.f_frsize,
            used_space=(stats.f_blocks - stats.f_bfree) * stats.f_frsize,
            available_space=stats.f_bavail * stats.f_frsize
        )
    except OSError:
        LOG.error('Failed to get storage status for mountpoint at: %s', mount_point)
    return state


def get_battery_status():
    """Gets the battery status of the BRCK device.

        Sample Response:
        {
            'state': 'CHARGING',
            'battery_level': 98
        }

    :return: dict
    """
    state = read_file('/tmp/battery/status') or STATE_UNKNOWN
    battery_level = read_file('/tmp/battery/capacity') or 0
    try:
        battery_level = int(battery_level)
    except ValueError:
        battery_level = 0
        LOG.error('Failed to ready battery capacity | Returned: %s', battery_level)
    state = dict(
        state=state.upper(),
        battery_level=battery_level
    )
    return state



def get_interface_speed(conn_name):
    """Calculates the up/down speed in bytes of a connection
    :return: tuple
    """
    up = down = 0
    state_path = 'network.%s.ifname' % (conn_name)
    iface_name = get_uci_state(state_path, command='get', as_dict=False)
    if iface_name != False:
        rx_path = '/sys/class/net/%s/statistics/rx_bytes' % (iface_name)
        tx_path = '/sys/class/net/%s/statistics/tx_bytes' % (iface_name)
        rx0 = read_file(rx_path)
        tx0 = read_file(tx_path)
        time.sleep(1)
        rx1 = read_file(rx_path)
        tx1 = read_file(tx_path)
        if not (False in [rx0, rx1, tx0, tx1]):
            up = int(tx1) - int(tx0)
            down = int(rx1) - int(rx0)
    return (up, down)


def get_network_status():
    """Gets the network state of the BRCK

    This is a summarized view of the connection state of the BRCK

    Sample Response:
            {
            "connected": true,
            "connection": {
            "connection_type": "WAN",
            "up_speed": 1000000,
            "down_speed": 1000000,
            "signal_strengh": 77
            },
            "connected_clients": 0
            }

    :return: dict
    """
    num_clients = 0
    connected = False
    net_type = STATE_UNKNOWN
    chilli_list = run_command(['connected_clients', 'list'], output=True)
    if chilli_list:
        num_clients = (chilli_list.splitlines().__len__() - 1)
    net_order = get_uci_state('brck.network.order', command='get', as_dict=False)
    active_net = None
    if net_order:
        nets = [n.strip() for n in net_order.split(' ')]
        net_state = get_uci_state('network')
        for net in nets:
            conn_state = net_state.get('network.{}.connected'.format(net), '') == '1'
            if conn_state:
                active_net = net
                net_type = net_state.get('network.{}.proto'.format(net), STATE_UNKNOWN).upper()
                break

    up, down = get_interface_speed(active_net)
    state = dict(
        connected = connected,
        connected_clients=num_clients,
        connection=dict(
            connection_type=net_type,
            up_speed=up,
            down_speed=down,
            signal_strength=get_signal_strength(net_type)
        )
    )
    return state


def get_system_state():
    mode = get_device_mode()
    storage_state = get_storage_status()
    battery_state = get_battery_status()
    power_state = get_soc_settings()
    network_state = get_network_status()
    state = dict(
        mode=mode,
        storage=storage_state,
        battery=battery_state,
        power=power_state,
        network=network_state
    )
    return state


def configure_system(config):
    """Configures the system
    """
    mconfig = {}
    mode = config.get('mode')
    if mode:
        mconfig['mode'] = mode
        uci_set('brck.power.mode', config['mode'])
    power = config.get('power', {})
    mconfig.update(power)
    validator = Validator(mconfig)
    has_time = 'on_time' in mconfig or 'off_time' in mconfig
    has_soc = 'soc_on' in mconfig or 'soc_off' in mconfig
    if mode:
        validator.ensure_inclusion('mode', DEVICE_MODES)
    if power:
        if has_time:
            validator.required_together('on_time', 'off_time')
            validator.ensure_format('on_time', REGEX_TIME)
            validator.ensure_format('off_time', REGEX_TIME)
            validator.ensure_less_than('on_time', 'off_time')
        if has_soc:
            validator.required_together('soc_on', 'soc_off')
            validator.ensure_range('soc_on', 1, 99, int)
            validator.ensure_range('soc_off', 1, 99, int)
            validator.ensure_less_than('soc_off', 'soc_on')
    if not validator.is_valid:
        return (422, validator.errors)
    if has_time:
        uci_set('brck.power.on_time', mconfig['on_time'])
        uci_set('brck.power.off_time', mconfig['off_time'])
    if has_soc:
        uci_set('brck.power.soc_on', mconfig['soc_on'])
        uci_set('brck.power.soc_off', mconfig['soc_off'])
    # Only commit uci if no errors
    uci_commit('brck.power')
    return (200, 'OK')