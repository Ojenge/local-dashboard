# -*- coding: utf-8 -*-
"""
Utilities for interacting with the filesystem.
"""

import os
import time
import psutil
try:
    import simplejson as json
except ImportError:
    import json

from brck.utils import run_command
from brck.utils import uci_get

from .soc import (get_soc_settings, get_firmware_version,
                  get_battery_temperature)
from .cache import cached, MINUTE, CACHE

LOG = __import__('logging').getLogger()

STATE_OK = 'OK'
STATE_ERROR = 'ERROR'
STATE_UNKNOWN = 'UNKNOWN'
STATE_NO_CONNECTION = 'NO CONNECTION'
DEVICE_MODES = ['MATATU', 'ALWAYS_ON', 'RETAIL', 'SOLAR_POWERED']
BRCK_PACKAGES = [
    '3g-monitor', 'battery-monitor', 'connected_clients', 'core-services',
    'gps-monitor', 'moja', 'moja-captive', 'python-brck-sdk', 'querymodem',
    'scan_wifi', 'supabrck-core'
]


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

    response = run_command(cmd_list, output=True) or ''
    if response is False:
        LOG.warn("No UCI state found at: %s", option)
        return {} if as_dict else False
    out = response
    if as_dict:
        out = dict()
        if not (response is False) and len(response):
            out.update(
                [l.replace("'", "").split('=') for l in response.splitlines()])
    return out


def get_signal_strength(net_type):
    """Get wireless signal strength (Mobile)

    :return: int (percentage 0-100)
    """
    if net_type == 'wan':
        signal_strength = 0
        model_id = run_command(['querymodem', 'model_id'], output=True)
        resp = run_command(['querymodem', 'signal'], output=True)
        try:
            rssi = int(resp or '')
            if model_id == 'MU736' or not model_id:
                if (rssi >= 0 and rssi <= 31):
                    signal_strength = (rssi * 827 + 127) >> 8
            else:
                signal_strength = 0 if (rssi == 255) else rssi
        except ValueError:
            LOG.error(
                "Failed to load signal strength: QueryModem Response: %s",
                resp)
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
    mode = STATE_UNKNOWN
    resp = uci_get('brck.soc.mode')
    if resp and len(mode):
        return mode
    return mode


@cached(timeout=(MINUTE * 60))
def get_storage_status(mount_point='/storage/data'):
    """Gets the disk storage status of a BRCK device in bytes.

    The default mountpoint `/storage/data`.

    Assumes that everything is mounted under /
    :return: dict
    """
    state = dict(total_space=0, used_space=0, available_space=0)
    try:
        stats = os.statvfs(mount_point)
        state = dict(
            total_space=stats.f_blocks * stats.f_frsize,
            used_space=(stats.f_blocks - stats.f_bfree) * stats.f_frsize,
            available_space=stats.f_bavail * stats.f_frsize)
    except OSError:
        LOG.error('Failed to get storage status for mountpoint at: %s',
                  mount_point)
    return state


@cached(timeout=(MINUTE * 5))
def get_battery_status(no_cache=False):
    """Gets the battery status of the BRCK device.

        Sample Response:
        {
            'state': 'CHARGING',
            'battery_level': 98
        }

    :return: dict
    """
    if no_cache:
        run_command(['check_battery'])

    state = read_file('/tmp/battery/status') or STATE_UNKNOWN
    battery_level = read_file('/tmp/battery/capacity') or 0
    extended = read_file('/tmp/battery/status_ex') or '{}'
    try:
        battery_level = int(battery_level)
        extended = json.loads(extended)
    except ValueError:
        battery_level = 0
        LOG.error('Failed to ready battery capacity | Returned: %s',
                  battery_level)
    state = dict(state=state.upper(), battery_level=battery_level)
    state.update(extended)
    if 'charging current' in state:
        state['charging_current'] = state['charging current']
        state.pop('charging current')
    if 'iadp' in state:
        state.pop('iadp')
    return state


def get_interface_speed(conn_name):
    """Calculates the up/down speed in bytes of a connection
    :return: tuple
    """
    up = down = 0
    if conn_name:
        state_path = 'network.%s.ifname' % (conn_name)
        cache_key = 'interface_speed_{}'.format(conn_name)
        previous_speed = CACHE.get(cache_key)
        iface_name = get_uci_state(state_path, command='get', as_dict=False)
        if iface_name != False:
            rx_path = '/sys/class/net/%s/statistics/rx_bytes' % (iface_name)
            tx_path = '/sys/class/net/%s/statistics/tx_bytes' % (iface_name)
            rx0 = read_file(rx_path)
            tx0 = read_file(tx_path)
            up1, down1, delta1 = new_speed = (int(rx0), int(tx0), time.time())
            if previous_speed:
                up0, down0, delta0 = previous_speed
                delta = delta1 - delta0
                up = int((up1 - up0) / delta)
                down = int((down1 - down0) / delta)
            CACHE.set(cache_key, new_speed)
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
    net_type = STATE_NO_CONNECTION
    chilli_list = run_command(['connected_clients', 'list'], output=True)
    if chilli_list:
        num_clients = (chilli_list.splitlines().__len__() - 1)
    net_order = get_uci_state(
        'brck.network.order', command='get', as_dict=False)
    active_net = None
    if net_order:
        nets = [n.strip() for n in net_order.split(' ')]
        net_state = get_uci_state('network')
        for net in nets:
            conn_state = net_state.get('network.{}.connected'.format(net),
                                       '') == '1'
            if conn_state:
                active_net = net
                net_type = net.upper()
                if net in ['wan', 'wan2']:
                    net_type = net_state.get('network.{}.proto'.format(net),
                                             STATE_UNKNOWN).upper()
                elif net == 'wwan':
                    net_type = 'Wireless'
                break

    up, down = get_interface_speed(active_net)
    state = dict(
        connected=connected,
        connected_clients=num_clients,
        connection=dict(
            connection_type=net_type,
            up_speed=up,
            down_speed=down,
            signal_strength=get_signal_strength(net_type)))
    return state


def get_system_state():
    """Gets the current system state for the dashboard API

    Includes storage status, battery status, power status and network state.

        See the API documentation for the expected payload schema.

    :return: dict
    """
    storage_state = get_storage_status()
    battery_state = get_battery_status()
    power_state = get_soc_settings()
    network_state = get_network_status()
    state = dict(
        storage=storage_state,
        battery=battery_state,
        power=power_state,
        network=network_state)
    return state


def get_software():
    """Gets the versions of the installed software on the system.
    
    This includes packages, firmware and operating system versions.

        See the REST API documentation for payload schema.

    :return: dict
    """
    os_version = run_command(
        ['uname', '-s', '-r', '-v', '-o'], output=True) or STATE_UNKNOWN
    # firmware_version = get_firmware_version()
    packages_text = run_command(['opkg', 'list-installed'], output=True) or ''
    package_data = dict(
        [p.split(' - ') for p in packages_text.splitlines() if p])
    # we're only interested in a subset of packages
    package_list = []
    for package_name in BRCK_PACKAGES:
        version = package_data.get(package_name)
        installed = version is not None
        package_list.append(
            dict(name=package_name, version=version, installed=installed))
    return dict(os=os_version, packages=package_list)


def get_firmware():
    """
    returns the firmware version
    :return: dict
    """
    firmware_version = get_firmware_version()
    return dict(firmware=firmware_version)


def get_os():
    """
    returns the os version
    :return:dict
    """
    os_version = run_command(
        ['uname', '-s', '-r', '-v', '-o'], output=True) or STATE_UNKNOWN

    return dict(os=os_version)


def get_diagnostics_data():
    """Gets diagnostics data on the SupaBRCK
    
    Includes:
    
    - temperature information
    - connected clients information
    
    :return: dict
    """
    status = {}
    client_data = run_command(['connected_clients'], output=True) or '{}'
    try:
        _data = json.loads(client_data)
        status['clients'] = _data.get('clients', [])
    except ValueError as exc:
        LOG.error('Failed to load connected_clients: %r', exc)
    modem_temp = run_command(['querymodem', 'temp'], output=True)
    try:
        status['modem'] = dict(temperature=[float(modem_temp)])
    except (ValueError, TypeError) as e:
        LOG.error('Failed to get modem temperature: %r', e)
        status['modem'] = dict(temperature=[STATE_UNKNOWN])
    bat_temp = get_battery_temperature()
    # cpu temperatures
    sensors_temp = psutil.sensors_temperatures() or {}
    cpu_temps = [t.current for t in sensors_temp.get('coretemp', [])]
    status['cpu'] = dict(temperature=cpu_temps)
    status['battery'] = dict(temperature=[bat_temp])
    return status


def get_modem_status():
    """
    get modem data
    :return: dict
    """
    modem_status = {}
    modem_temp = run_command(['querymodem', 'temperature'], output=True)
    modem_signal = run_command(['querymodem', 'signal'], output=True)

    modem_status['temperature'] = modem_temp
    modem_status['signal'] = modem_signal
    return modem_status


def get_power_data():
    """ 
    Gets the Power data for the api as per specifications
    Includes:
        -battery voltage
        -charge voltage
        -charging status
        -battery temperature
        -MCU temperature
        -unit temperature
        -charging current
        -whether charger is connected

    return: dict
    """
    bat_stats = get_battery_status()

    battery_stats = dict(
        charge_percentage=bat_stats('capacity'),
        charging_status=bat_stats('status'),
        charging_current=bat_stats('charging_current'),
        charge_voltage=bat_stats('voltage'))

    return battery_stats
