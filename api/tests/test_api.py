# -*- coding: utf-8 -*-

import sys
import os
import json
import pytest
import mock
from datetime import datetime
from datetime import timedelta

import local_api
from local_api.apiv1 import models

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

DUMMY_CHILLY_RESP = """Station                Connected time 	Signal         	Inactive time  	RX bytes       	TX Bytes       
34:13:e8:3e:d0:7d      1044           	-27            	10             	680540         	1229742"""


DUMMY_SIGNAL_RESP = "24"
TEST_DATABASE_PATH = '/tmp/testdb.sqlite'
TEST_DATABASE_URL = 'sqlite:///%s' % (TEST_DATABASE_PATH)

EXPECTED_NETWORK_RESP = dict(
    connected=False,
    connected_clients=1,
    connection=dict(
        connection_type='3G',
        up_speed=0,
        down_speed=0,
        signal_strength=100
    )
)

TEST_USER = 'test_user'
TEST_PASSWORD = 'test_password'

@pytest.fixture
def client(request):
    if os.path.exists(TEST_DATABASE_PATH):
        os.unlink(TEST_DATABASE_PATH)
    local_api.app.config['SQLALCHEMY_DATABASE_URI'] = TEST_DATABASE_URL
    t_client = local_api.app.test_client()
    return t_client

@pytest.fixture
def headers():
    # initialize user
    local_api.db.create_all()
    models.HASH_ROUNDS = 1
    assert models.create_user(TEST_USER, TEST_PASSWORD)
    _token = models.make_token(TEST_USER)
    return {'X-Auth-Token-Key': _token['token']}


@pytest.fixture
def expired_headers():
    local_api.db.create_all()
    models.HASH_ROUNDS = 1
    assert models.create_user(TEST_USER, TEST_PASSWORD)
    _token = models.AuthToken(principal_id=TEST_USER)
    _token.expiry = datetime.utcnow()
    local_api.db.session.add(_token)
    local_api.db.session.commit()
    return {'X-Auth-Token-Key': _token.token}


def load_json(response):
    """Load JSON from response"""
    return json.loads(response.data.decode('utf8'))

def test_get_auth_token(client, headers):
    _auth = dict(login=TEST_USER, password=TEST_PASSWORD)
    resp = client.post('/api/v1/auth',
                       content_type='application/json',
                       data=json.dumps(_auth))
    assert resp.status_code == 200
    payload = load_json(resp)
    assert 'token' in payload
    assert 'expiry' in payload 


def test_unauthorized(client):
    local_api.db.create_all()
    resp = client.get('/api/v1/system')
    assert resp.status_code == 401


def test_ping(client):
    resp = client.get('/api/v1/ping')
    assert resp.status_code == 200


def test_expired_token(client, expired_headers):
    resp = client.get('/api/v1/system', headers=expired_headers)
    assert resp.status_code == 401


def test_system_api(client, headers):
    with mock.patch('local_api.apiv1.utils.get_interface_speed', side_effect=[(0, 0)]):
        resp = client.get('/api/v1/system', headers=headers)
        assert resp.status_code == 200
        payload = load_json(resp)
        assert isinstance(payload, dict)
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


def test_system_battery_api(client, headers):
    with mock.patch('local_api.apiv1.utils.get_interface_speed', side_effect=[(0, 0)]):
        with mock.patch('local_api.apiv1.utils.uci_get', side_effects=['ALWAYS_ON']):
            with mock.patch('local_api.apiv1.utils.run_command',
                side_effect=[DUMMY_CHILLY_RESP, DUMMY_WAN_STATE_RESP, DUMMY_SIGNAL_RESP]):
                with mock.patch('local_api.apiv1.utils.read_file', side_effect=['CHARGING', '98']):
                    resp = client.get('/api/v1/system', headers=headers)
                    assert(resp.status_code == 200)
                    payload = load_json(resp)
                    assert 'battery' in payload
                    assert payload['battery'] == dict(state='CHARGING', battery_level=98)


def test_network_status_api(client, headers):
    with mock.patch('local_api.apiv1.utils.get_interface_speed', side_effect=[(0, 0)]):
        with mock.patch('local_api.apiv1.utils.uci_get', side_effects=['ALWAYS_ON']):
            with mock.patch('local_api.apiv1.utils.run_command',
                            side_effect=[DUMMY_CHILLY_RESP, DUMMY_WAN_STATE_RESP, '31']):
                with mock.patch('local_api.apiv1.utils.read_file', side_effect=['CHARGING', '98']):
                    resp = client.get('/api/v1/system', headers=headers)
                    assert resp.status_code == 200
                    payload = load_json(resp)
                    assert 'network' in payload
                    assert payload['network'] == EXPECTED_NETWORK_RESP


def test_patch_system_ok(client, headers):
    test_payload = dict(
        mode='ALWAYS_ON',
        power=dict(
            on_time='06:00',
            off_time='22:00',
            soc_on=15,
            soc_off=5
        )
    )
    with mock.patch('local_api.apiv1.utils.get_interface_speed', side_effect=[(0, 0)]):
        with mock.patch('local_api.apiv1.utils.uci_get', side_effects=['ALWAYS_ON']):
            with mock.patch('local_api.apiv1.utils.uci_set', return_value=True):
                with mock.patch('local_api.apiv1.utils.run_command',
                                side_effect=[DUMMY_CHILLY_RESP, DUMMY_WAN_STATE_RESP, DUMMY_SIGNAL_RESP]):
                    with mock.patch('local_api.apiv1.utils.read_file', side_effect=['CHARGING', '98']):
                        resp = client.patch('/api/v1/system',
                                            data=json.dumps(test_payload),
                                            content_type='application/json',
                                            headers=headers)
                        assert resp.status_code == 200
                        payload = load_json(resp)
                        assert 'mode' in payload
                        assert 'battery' in payload
                        assert 'network' in payload


def test_patch_system_not_ok(client, headers):
    test_payload = dict(
        mode='ALWAYS_ON',
        power=dict(
            on_time='06:00',
            off_time='22:00',
            soc_on=15,
            soc_off=25
        )
    )
    with mock.patch('local_api.apiv1.utils.uci_get', side_effect=['ALWAYS_ON']):
        with mock.patch('local_api.apiv1.utils.uci_set', return_value=True):
            with mock.patch('local_api.apiv1.utils.run_command',
                            side_effect=[DUMMY_CHILLY_RESP, DUMMY_WAN_STATE_RESP, DUMMY_SIGNAL_RESP]):
                with mock.patch('local_api.apiv1.utils.read_file', side_effect=['CHARGING', '98']):
                    resp = client.patch('/api/v1/system',
                                        data=json.dumps(test_payload),
                                        content_type='application/json',
                                        headers=headers)
                    payload = load_json(resp)
                    assert 'errors' in payload
                    errors = payload['errors']
                    assert 'soc_off' in errors
                    assert 'soc_on' in errors
                    assert resp.status_code == 422


def test_get_sim_networks(client, headers):
    resp = client.get('/api/v1/networks/sim/',
                      headers=headers)
    assert resp.status_code == 200
    payload = load_json(resp)
    assert payload[0]['id'] == 'SIM1'
    assert payload[1]['id'] == 'SIM2'
    assert payload[2]['id'] == 'SIM3'


def test_get_sim_network(client, headers):
    resp = client.get('/api/v1/networks/sim/SIM1',
                      headers=headers)
    assert resp.status_code == 200
    payload = load_json(resp)
    assert payload['id'] == 'SIM1'
    assert payload['name'] == 'SIM 1'


def test_patch_sim(client, headers):
    test_payload = dict(
        configuration=dict(
            pin="1234",
            network=dict(
                apn="internet"
            )
        )
    )
    with mock.patch('local_api.apiv1.sim.run_command', side_effect=['OK']):
        with mock.patch('local_api.apiv1.sim.uci_set', side_effect=[True]):
            with mock.patch('local_api.apiv1.sim.uci_commit', side_effect=[True]):
                resp = client.patch('/api/v1/networks/sim/SIM1',
                                    content_type='application/json',
                                    data=json.dumps(test_payload),
                                    headers=headers)
                payload = load_json(resp)
                print payload
                assert resp.status_code == 200
