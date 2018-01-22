# -*- coding: utf-8 -*-

import sys
import os
import json
import pytest
import mock

import local_api

# inject syspath
file_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(file_dir, '../'))


DUMMY_WAN_STATE_RESP = """network.wan=interface
network.wan.proto='3g'
network.wan.pppd_options='noipdefault lcp-echo-interval 10 lcp-echo-failure 5'
network.wan.auto='1'
network.wan.apn='internet'
network.wan.up='1'
network.wan.device='ppp0'
network.wan.ifname='3g-wan'
network.wan.connected='0'"""

DUMMY_CHILLY_RESP = """34-13-E8-3E-D0-7D 192.168.180.2 dnat 5a65a0a200000001 0 - 0/0 0/0 0/0 0/0 0 0 0/0 0/0 -
78-F8-82-D0-E3-84 192.168.180.3 dnat 5a659c2000000002 0 - 0/0 0/0 0/0 0/0 0 0 0/0 0/0 -"""

DUMMY_SIGNAL_RESP = "24"

EXPECTED_NETWORK_RESP = dict(
    connected=False,
    connected_clients=2,
    connection=dict(
        connection_type='3G',
        up_speed=0,
        down_speed=0,
        signal_strength=24
    )
)

@pytest.fixture
def client(request):
    print request
    client =  local_api.app.test_client()
    return client

def load_json(response):
    """Load JSON from response"""
    return json.loads(response.data.decode('utf8'))



def test_system_api(client):
    resp = client.get('/api/v1/system')
    assert(resp.status_code == 200)
    payload = load_json(resp)
    assert(isinstance(payload, dict))
    print payload
    assert 'storage' in payload
    storage_payload = payload['storage']
    for k in ['total_space', 'used_space', 'available_space']:
        v = storage_payload.get(k)
        assert v is not None and isinstance(v, int)
    assert 'battery' in payload
    battery_payload = payload['battery']
    for k in ['state', 'battery_level']:
        v = battery_payload.get(k)
        assert v is not None


def test_system_battery_api(client):
    with mock.patch('local_api.apiv1.utils.run_command',
        side_effect=[True, DUMMY_CHILLY_RESP, DUMMY_WAN_STATE_RESP, DUMMY_SIGNAL_RESP]):
        with mock.patch('local_api.apiv1.utils.read_file', side_effect=['CHARGING', '98']):
            resp = client.get('/api/v1/system')
            assert(resp.status_code == 200)
            payload = load_json(resp)
            assert 'storage' in payload
            assert payload['battery'] == dict(state='CHARGING', battery_level=98)


def test_network_status_api(client):
    with mock.patch('local_api.apiv1.utils.run_command',
        side_effect=[True, DUMMY_CHILLY_RESP, DUMMY_WAN_STATE_RESP, DUMMY_SIGNAL_RESP]):
        with mock.patch('local_api.apiv1.utils.read_file', side_effect=['CHARGING', '98']):
            resp = client.get('/api/v1/system')
            assert(resp.status_code == 200)
            payload = load_json(resp)
            assert 'network' in payload
            assert payload['network'] == EXPECTED_NETWORK_RESP
        
