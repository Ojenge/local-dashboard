# -*- coding: utf-8 -*-

"""
Utilities for interacting with the filesystem.
"""

import os
from brck.utils import run_command


LOG = __import__('logging').getLogger()

STATE_OK = 'OK'
STATE_ERROR = 'ERROR'
STATE_UNKNOWN = 'UNKNOWN'



def get_uci_state(option, command='show'):
    """Gets the uci state stored at `option`

    :param str option: the name of the uci option
    :param str command: the command to run on state (`show` or `get`)
    :param bool expand_options: whether the response should be expanded
    :return: dict of the state
    """
    cmd_list = ['uci', '-P']
    cmd_list.append('/var/state')

    cmd_list.append(command)
    cmd_list.append(option)

    response = run_command(cmd_list, output=True)
    out = dict()
    if not(response is False) and len(response):
        out.update([l.replace("'", "").split('=') for l in response.splitlines()])
    return out


def get_signal_strength():
    """Get wireless signal strength (Mobile)

    :return: int (percentage 0-100)
    """
    signal_strengh = 0
    resp = run_command(['querymodem', 'signal'])
    try:
        signal_strengh = int(resp or '')
    except ValueError:
        LOG.error("Failed to load signal strength: QueryModem Response: %s", resp)
    return signal_strengh


def read_file(path):
    """Reads the file contents at `path`

    :param str path: the the path to read
    :return: str contents of the file or False if file reading failed
    """
    contents = False
    try:
        with open(path) as f:
            contents = f.read()
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
    return 'UNKNOWN'


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
    battery_level = 0
    state = 'UNKNOWN'
    check_resp = run_command('check_battery', output=False)
    if check_resp:
        state = read_file('/tmp/battery/status') or STATE_UNKNOWN
        capacity = read_file('/tmp/battery/capacity')
        try:
            battery_level = int(capacity)
        except ValueError:
            LOG.error('Failed to ready battery capacity | Returned: %s', capacity)
    state = dict(
        state=state.upper(),
        battery_level=battery_level
    )
    return state


def get_power_config():
    """Gets the power configuration on the BRCK

    Example:

        {
            'soc_on': 0,
            'soc_off': 0,
            'turn_on_time': "00:00",
            'turn_off_time': "00:00"
        }

    Depending on the device mode, the configuration determines
    power on and power off behaviour.
    :return: dict
    """
    return {}


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
    chilli_list = run_command(['chilli_query', 'list'], output=True)
    if chilli_list:
        num_clients = chilli_list.splitlines().__len__()
    uci_state = get_uci_state('network.wan')
    net_type = uci_state.get('network.wan.proto', STATE_UNKNOWN).upper()
    state = dict(
        connected=uci_state.get('network.wan.connected', '') == '1',
        connected_clients=num_clients,
        connection=dict(
            connection_type=net_type,
            up_speed=0,
            down_speed=0,
            signal_strength=get_signal_strength()
        )
    )
    return state


