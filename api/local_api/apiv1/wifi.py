# -*- coding: utf-8 -*-

"""
WiFi bridge/ap connection management utilities.
"""

from brck.utils import (
    uci_get,
    uci_set,
    uci_commit,
    run_command
)
from .utils import get_uci_state
from .schema import Validator
from .errors import APIError

LOG = __import__('logging').getLogger()

CONNECTION_IDS = ['WIFI1']
RADIO_UCI = {
    'WIFI1': 'wireless.radio1.path'
}
CONNECTION_NAMES = {
    'WIFI1': 'Wireless 1'
}
STATE_NOT_CONFIGURED = 'NOT_CONFIGURED'
STATE_NONE = 'none'
STATE_AUTO = 'auto'
MODE_AP = 'ap'
MODE_STA = 'sta'

RADIO_CONFIGS = ['hwmode', 'channel']

def validate_channel(channel):
    """validates wireless channel
    """
    assert channel == 'auto' or (int(channel) >= 1 and int(channel) <= 196)


def get_wireless_config(wifi_id=None):
    """Gets the current wireless configuration.

    We assume that there's only one extra wireless interface.

    :return list(dict):
    # """
    net_info = []
    conn_ids = [wifi_id] if wifi_id else CONNECTION_IDS
    for conn_id in conn_ids:
        net_state = get_uci_state('wireless')
        available = bool(net_state.get(RADIO_UCI[conn_id]))
        connected = False
        info = {}
        if available:
            connected =  uci_get('network.wwan.connected') == '1'
            info['ssid'] = net_state.get('wireless.wifibridge.ssid') or STATE_NOT_CONFIGURED 
            info['encryption'] = net_state.get('wireless.wifibridge.encryption', STATE_NONE)
            info['mode'] = net_state.get('wireless.wifibridge.mode') or STATE_NOT_CONFIGURED
            info['hidden'] = net_state.get('wireless.wifibridge.hidden', '0')
            info['channel'] = net_state.get('wireless.radio1.channel') or STATE_AUTO
            info['hwmode'] = net_state.get('wireless.radio1.hwmode')
            info['network'] = {}
        net_info.append(dict(
            id=conn_id,
            name=CONNECTION_NAMES[conn_id],
            available=available,
            connected=connected,
            info=info
        ))
    return net_info



def apply_wifi_configuration(config):
    """Applies wireless configuration to UCI.

    Also reloads wireless.


    :param dict config:

    :return: None
    """
    if uci_get('mwan3.wwan.enabled') != '1':
        LOG.warn('Enabling wwan interface')
        uci_set('mwan3.wwan.enabled', '1')
        uci_commit('mwan3')
    base_bridge_path = 'wireless.wifibridge.{}'
    base_radio_path = 'wireless.radio1.{}'
    mode = config['mode']
    if mode == MODE_STA:
        config['hidden'] = '1'
    for k,v in config.iteritems():
        if v:
            uci_path = (
                base_radio_path.format(k) 
                if k in RADIO_CONFIGS else
                base_bridge_path.format(k)
            )
            LOG.warn('configuring wireless [%s] | [%s]', uci_path, v)
            uci_set(uci_path, v)
    uci_commit('wireless')
    LOG.warn('Reloading Network')
    run_command(['wifi', 'reload'])


def configure_wifi(wifi_id, payload):
    """Configure wireless network.
    
    See the API documentation for expected configuration payload schema.

    :param string wifi_id: wifi id
    :param dict payload: configuration payload

    :return: tuple
    """
    available = bool(uci_get(RADIO_UCI[wifi_id]))
    if not available:
        raise APIError(message='Device not found', status_code=422)
    config = payload.get('configuration', {})
    v = Validator(config)
    v.ensure_exists('mode', 'ssid')
    v.ensure_inclusion('mode', [MODE_AP, MODE_STA])
    v.ensure_inclusion('encryption', ['none', 'psk', 'psk2', 'wep', 'wpa'],
                       required=False)
    if config.get('encryption') != 'none':
        v.ensure_exists('key')
    v.ensure_passes_test('channel', validate_channel, required=False)
    v.ensure_inclusion('hidden', ['0', '1'], required=False)
    v.ensure_inclusion('hwmode', ['11a', '11b', '11g'], required=False)
    if v.is_valid:
        apply_wifi_configuration(config)
        return (200, 'OK')
    else:
        return (422, v.errors)