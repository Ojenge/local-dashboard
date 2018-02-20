# -*- coding: utf-8 -*-

"""Ethernet connection management on the SupaBRCK

At the moment, the SupaBRCK only supports one ethernet connection.
"""

import os
import time
import socket
import psutil

from brck.utils import (
    uci_get,
    uci_set,
    uci_delete,
    uci_commit,
    run_command,
    LOG
)

from .errors import APIError
from .utils import get_uci_state
from .schema import Validator

# LOG = __import__('logging').getLogger()

NETWORKS = ['ETHERNET1']
CONNECTION_MAP = {
    'ETHERNET1': 'lan'
}
CONNECTION_NAMES = {
    'ETHERNET1': 'ETHERNET 1'
}
NETWORK_CONFIG_WAIT_TIME = 5
if os.getenv('FLASK_TESTING'):
    NETWORK_CONFIG_WAIT_TIME = 0


def get_ethernet_networks(net_id=None):
    """Gets the connection status for the provided network or all networks.

    The output response schema is described in the API documentation under
    ethernet connections.

    :return: dict
    """
    networks = [net_id] if (net_id is not None) else NETWORKS
    networks_info = []
    for net in networks:
        interface = CONNECTION_MAP.get(net, None)
        if interface is None:
            raise APIError(status_code=404, errors=[dict(network="not found")])
        uci_path = 'network.{}'.format(interface)
        uci_state = get_uci_state(uci_path)
        connected = uci_state.get('network.{}.connected'.format(interface)) == '1'
        available = uci_state.get('network.{}.up'.format(interface)) == '1'
        dhcp_enabled = uci_state.get('network.{}.proto'.format(interface)) == 'dhcp'
        network_device = uci_state.get('network.{}.ifname'.format(interface))
        net_data = dict(id=net,
                        name=CONNECTION_NAMES[net],
                        available=available,
                        connected=connected)
        net_info = {}
        all_addr_info = psutil.net_if_addrs()
        interface_info = all_addr_info.get(network_device, None)
        if interface_info:
            ipv4 = filter(lambda s: s.family == socket.AF_INET, interface_info)
            if len(ipv4) == 1:
                net_info.update(
                    dict(
                        ipaddr=ipv4[0].address,
                        netmask=ipv4[0].netmask
                    )
                )
        # get uci dns/routing configuration
        net_info['dns'] = uci_get('network.{}.dns'.format(interface)) or ''
        net_info['gateway'] = uci_get('network.{}.gateway'.format(interface)) or ''
        ip_info = dict(dhcp_enabled=dhcp_enabled,
                       network=net_info)
        net_data['info'] = ip_info        
        networks_info.append(net_data)
    return networks_info


def configure_ip(net_id, dhcp_enabled, net_info):
    """Configures ethernet IP configuration.

    Reloads the network.
    """
    interface = CONNECTION_MAP.get(net_id)
    if dhcp_enabled:
        LOG.warn('Configuring interface [%s] proto to DHCP', interface)
        uci_set('network.{}.proto'.format(interface), 'dhcp')
        for static_key in ['ipaddr', 'netmask', 'gateway', 'dns']:
            uci_option = 'network.{}.{}'.format(interface, static_key)
            LOG.warn('Deleting UCI option:[%s]', uci_option)
            uci_delete(uci_option)
    else:
        net_info['proto'] = 'static'
        for k,v in net_info.iteritems():
            if v:
                uci_option = 'network.{}.{}'.format(interface, k)
                LOG.warn('Configuring network: [%s = %s]', uci_option, v)
                uci_set(uci_option, v)
    uci_commit('network.{}'.format(interface))
    run_command(['iptables', '--flush'])
    run_command(['/etc/init.d/network', 'reload'])
    run_command(['iptables', '--flush'])
    LOG.warn('Sleeping for five (5) seconds to see if interface connection comes up.')
    time.sleep(NETWORK_CONFIG_WAIT_TIME)
    return (200, 'OK')



def dns_server_check(server_names):
    """Validates dns server names provided.

    We try ensure that each server name is valid.
    
    Raises a socket error if any of the provided names is invalid.

    :params str server_names: comma separated list of server names.

    :return: None 
    """
    if server_names:
        names = server_names.split(',')
        for name in names:
            socket.gethostbyname(name)


def configure_ethernet(net_id, payload):
    """Configure ethernet connection.

    Receives a payload:

        {
        "configuration": {
            "dhcp_enabled": true,
            "network_info": {
                "static_ip": "10.10.10.10",
                "default_route": "10.10.10.1",
                "subnet_mask": "255.255.255.0",
                "dns_servers": "8.8.8.8,mydns.com"
            }
        }
        }
    :return: (int, str) | (int, list)
    """
    config = payload.get('configuration', {})
    net_info = config.get('network', {})
    validator_data = {}
    dhcp_enabled = config.get('dhcp_enabled', '')
    validator_data['dhcp_enabled'] = dhcp_enabled
    validator_data.update(net_info)
    v = Validator(validator_data)
    v.ensure_inclusion('dhcp_enabled', [True, False])
    if v.is_valid and dhcp_enabled == False:
        # validate ip configuration
        v.ensure_exists('ipaddr', 'netmask')
        v.ensure_passes_test('ipaddr', socket.inet_aton)
        v.ensure_passes_test('netmask', socket.inet_aton)
        v.ensure_passes_test('gateway', socket.inet_aton, required=False)
        v.ensure_passes_test('dns', dns_server_check)
        # TODO - DNS Servers
    if v.is_valid:
        # apply uci changes
        return configure_ip(net_id, dhcp_enabled, net_info)
    else:
        return (422, v.errors)