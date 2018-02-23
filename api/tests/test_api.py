# -*- coding: utf-8 -*-

import sys
import os
import json
import pytest
import mock
from datetime import datetime
from psutil._common import shwtemp, snic

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
network.wan.connected='1'"""

DUMMY_CHILLY_RESP = """Station                Connected time 	Signal         	Inactive time  	RX bytes       	TX Bytes       
34:13:e8:3e:d0:7d      1044           	-27            	10             	680540         	1229742"""

DUMMY_NETWORK_ORDER = 'wan lan'
DUMMY_SIGNAL_RESP = "24"
DUMMY_STATE = [DUMMY_CHILLY_RESP, DUMMY_NETWORK_ORDER, DUMMY_WAN_STATE_RESP, DUMMY_SIGNAL_RESP]
BATTERY_SIDE_EFFECTS = ['CHARGING', '98', u'{"charging current": 0, "voltage": 12}']
CONNECTED_CLIENTS_SIDE_EFFECT = ('{ "clients": [ { "mac_address": "34:13:e8:3e:d0:7d",'
    ' "name": "Unknown", "ip": "192.168.180.3", "connected_time": "88", "idle_time": "10",'
    '"rx_bytes": "130425", "tx_bytes": "149626", "signal": "-45 dBm" } ] }')
CONNECTED_CLIENT_PARSED ={
    u'connected_time': u'88',
    u'idle_time': u'10',
    u'ip': u'192.168.180.3',
    u'mac_address': u'34:13:e8:3e:d0:7d',
    u'name': u'Unknown',
    u'rx_bytes': u'130425',
    u'signal': u'-45 dBm',
    u'tx_bytes': u'149626'}
BAX_SIDE_EFFECT = (
    u'{"at_rate":0,"at_rate_ok":1,"at_rate_empty":-1,"at_rate_full":-1,'
    u'"temperature":32,"avg_current":0,"max_error":1,"relative_soc":100'
    u',"absolute_soc":103,"current":0,"voltage":8329,"status":231,"mode":1'
    u',"cycle_count":19,"design_cap":4050,"design_voltage":7400,"spec":49'
    u',"serial":1673,"dev_chem":" LION",'
    u'"manufacturer":" WTE        ","manu_data":" P nnnnnnnnnnnn",}')
PSUTIL_TEMP_SIDE_EFFECT = {'coretemp': [shwtemp(label='Core 0', current=55.0, high=110.0, critical=110.0),
                                        shwtemp(label='Core 2', current=56.0, high=110.0, critical=110.0)]}
EXPECTED_BAT_TEMPERATURE = [32.0]
EXPECTED_CPU_TEMPERATURE = [55.0, 56.0]
# WAN
DISCONNECTED_UCI_STATE = """network.lan=interface
network.lan.ifname='eth0'
network.lan.proto='dhcp'
network.lan.macaddr='42:1d:12:35:c6:36'
network.lan.connected='0'"""
CONNECTED_UCI_STATE = """network.lan=interface
network.lan.ifname='eth0'
network.lan.proto='dhcp'
network.lan.macaddr='42:1d:12:35:c6:36'
network.lan.up='1'
network.lan.device='eth0'
network.lan.connected='1'"""
DUMMY_PSUTIL_IF_ADDR = {
    'eth0': [snic(family=2, address='192.168.180.3', netmask='255.255.255.0', broadcast='192.168.180.255', ptp=None)]
}
EXPECTED_ETHERNET1_DISCONNECTED = dict(
    id='ETHERNET1',
    name='ETHERNET 1',
    available=False,
    connected=False,
    info=dict(
        dhcp_enabled=True,
        network=dict(
            ipaddr='192.168.180.3',
            netmask='255.255.255.0',
            gateway='',
            dns=''
        )
    )
)
EXPECTED_ETHERNET1_CONNECTED = dict(
    id='ETHERNET1',
    name='ETHERNET 1',
    available=True,
    connected=True,
    info=dict(
        dhcp_enabled=True,
        network=dict(
            ipaddr='192.168.180.3',
            netmask='255.255.255.0',
            gateway='',
            dns=''
        )
    )
)


# TEST DATABASE SETUP
TEST_DATABASE_PATH = './testdb.sqlite3'
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
ROOT_USER = 'root'
ROOT_PASSWORD = 'fakepass'
EXPECTED_BATTERY =  dict(state='CHARGING',
                         battery_level=98,
                         charging_current=0,
                         voltage=12)


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
    local_api.db.drop_all()
    local_api.db.create_all()
    models.HASH_ROUNDS = 1
    assert models.create_user(TEST_USER, TEST_PASSWORD)
    assert models.create_user(ROOT_USER, ROOT_PASSWORD)
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
    assert payload['password_changed'] == False


@pytest.mark.skipif(sys.platform == 'darwin',
                    reason="spwd not available on MAC")
def test_get_auth_token_as_system_user(client, headers):
    _auth = dict(login=ROOT_USER, password=ROOT_PASSWORD)
    with mock.patch('local_api.apiv1.models.check_system_login',
                    side_effect=[True]):
        resp = client.post('/api/v1/auth',
                           content_type='application/json',
                           data=json.dumps(_auth))
        assert resp.status_code == 200
        payload = load_json(resp)
        assert 'token' in payload
        assert 'expiry' in payload
        assert payload['password_changed'] == True


def test_unauthorized(client):
    local_api.db.create_all()
    resp = client.get('/api/v1/system')
    assert resp.status_code == 401


def test_ping(client):
    resp = client.get('/api/v1/ping')
    assert resp.status_code == 200


def _test_expired_token(client, expired_headers):
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
                            side_effect=DUMMY_STATE):
                with mock.patch('local_api.apiv1.utils.read_file', side_effect=BATTERY_SIDE_EFFECTS):
                    resp = client.get('/api/v1/system', headers=headers)
                    assert(resp.status_code == 200)
                    payload = load_json(resp)
                    assert 'battery' in payload
                    assert payload['battery'] == EXPECTED_BATTERY


def test_network_status_api(client, headers):
    with mock.patch('local_api.apiv1.utils.get_interface_speed', side_effect=[(0, 0)]):
        with mock.patch('local_api.apiv1.utils.uci_get', side_effects=['ALWAYS_ON']):
            with mock.patch('local_api.apiv1.utils.run_command',
                            side_effect=[DUMMY_CHILLY_RESP, DUMMY_NETWORK_ORDER, DUMMY_WAN_STATE_RESP, '31']):
                with mock.patch('local_api.apiv1.utils.read_file', side_effect=BATTERY_SIDE_EFFECTS):
                    resp = client.get('/api/v1/system', headers=headers)
                    assert resp.status_code == 200
                    payload = load_json(resp)
                    assert 'network' in payload
                    assert payload['network'] == EXPECTED_NETWORK_RESP


def test_patch_system_ok(client, headers):
    test_payload = dict(
        power=dict(
            mode='ALWAYS_ON',
            on_time='06:00',
            off_time='22:00',
            soc_on=15,
            soc_off=5
        )
    )
    with mock.patch('local_api.apiv1.soc.set_soc', side_effect=[True]):
        resp = client.patch('/api/v1/system',
                            data=json.dumps(test_payload),
                            content_type='application/json',
                            headers=headers)
        assert resp.status_code == 200


def test_get_power_config_not_configured(client, headers):
    not_configured = dict(configured=False, mode=None, battery=EXPECTED_BATTERY)
    with mock.patch('local_api.apiv1.utils.read_file', side_effect=BATTERY_SIDE_EFFECTS):
        with mock.patch('local_api.apiv1.soc.get_power_config',
                        side_effect=[not_configured]):
            resp = client.get('/api/v1/power',
                            content_type='application/json',
                            headers=headers)
            assert resp.status_code == 200
            payload = load_json(resp)
            assert payload == not_configured


def test_get_power_config_configured(client, headers):
    configured = dict(configured=True,
                      mode='ALWAYS_ON',
                      battery=EXPECTED_BATTERY)
    with mock.patch('local_api.apiv1.soc.uci_get',
                    side_effect=['ALWAYS_ON']):
        with mock.patch('local_api.apiv1.utils.read_file', side_effect=BATTERY_SIDE_EFFECTS):
            resp = client.get('/api/v1/power',
                            content_type='application/json',
                            headers=headers)
            assert resp.status_code == 200
            payload = load_json(resp)
            assert payload == configured


def test_patch_system_not_ok(client, headers):
    test_payload = dict(
        power=dict(
            mode='ALWAYS_ON',
            on_time='06:00',
            off_time='22:00',
            soc_on=15,
            soc_off=25
        )
    )
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
        with mock.patch('local_api.apiv1.sim.connect_sim', side_effect=[{}]):
            resp = client.patch('/api/v1/networks/sim/SIM1',
                                content_type='application/json',
                                data=json.dumps(test_payload),
                                headers=headers)
            assert resp.status_code == 200
            assert load_json(resp)


def test_get_ethernet_networks(client, headers):
    with mock.patch('local_api.apiv1.utils.run_command',
                    side_effect=[DISCONNECTED_UCI_STATE]):
        with mock.patch('local_api.apiv1.ethernet.psutil.net_if_addrs',
                       side_effect=[DUMMY_PSUTIL_IF_ADDR]):
            resp = client.get('/api/v1/networks/ethernet/',
                            headers=headers)
            assert resp.status_code == 200
            payload = load_json(resp)
            assert payload[0] == EXPECTED_ETHERNET1_DISCONNECTED


def test_get_ethernet_networks_single(client, headers):
    with mock.patch('local_api.apiv1.utils.run_command',
                    side_effect=[DISCONNECTED_UCI_STATE]):
        with mock.patch('local_api.apiv1.ethernet.psutil.net_if_addrs',
                       side_effect=[DUMMY_PSUTIL_IF_ADDR]):
            resp = client.get('/api/v1/networks/ethernet/ETHERNET1',
                            headers=headers)
            assert resp.status_code == 200
            payload = load_json(resp)
            assert payload == EXPECTED_ETHERNET1_DISCONNECTED


def test_get_ethernet_networks_connected(client, headers):
    with mock.patch('local_api.apiv1.utils.run_command',
                    side_effect=[CONNECTED_UCI_STATE]):
        with mock.patch('local_api.apiv1.ethernet.psutil.net_if_addrs',
                       side_effect=[DUMMY_PSUTIL_IF_ADDR]):
            resp = client.get('/api/v1/networks/ethernet/ETHERNET1',
                            headers=headers)
            assert resp.status_code == 200
            payload = load_json(resp)
            assert payload == EXPECTED_ETHERNET1_CONNECTED


def test_get_ethernet_networks_unknown(client, headers):
    with mock.patch('local_api.apiv1.utils.run_command',
                    side_effect=[DISCONNECTED_UCI_STATE]):
        resp = client.get('/api/v1/networks/ethernet/ETHERNET9',
                          headers=headers)
        assert resp.status_code == 404
        assert load_json(resp)


def test_patch_ethernet_dhcp(client, headers):
    test_payload = dict(
        configuration=dict(
            dhcp_enabled=True
        )
    )
    with mock.patch('local_api.apiv1.utils.run_command',
                    side_effect=[DISCONNECTED_UCI_STATE]):
        with mock.patch('local_api.apiv1.ethernet.psutil.net_if_addrs',
                       side_effect=[DUMMY_PSUTIL_IF_ADDR]):
            resp = client.patch('/api/v1/networks/ethernet/ETHERNET1',
                                content_type='application/json',
                                data=json.dumps(test_payload),
                                headers=headers)
            assert resp.status_code == 200
            payload = load_json(resp)
            assert payload == EXPECTED_ETHERNET1_DISCONNECTED


def test_patch_ethernet_static(client, headers):
    test_payload = dict(
        configuration=dict(
            dhcp_enabled=False,
            network=dict(
                ipaddr='192.168.0.101',
                netmask='255.255.255.0',
                gateway='192.168.0.1',
                dns='8.8.8.8,localhost'
            )
        )
    )
    with mock.patch('local_api.apiv1.utils.run_command',
                    side_effect=[DISCONNECTED_UCI_STATE]):
        with mock.patch('local_api.apiv1.ethernet.psutil.net_if_addrs',
                       side_effect=[DUMMY_PSUTIL_IF_ADDR]):
                resp = client.patch('/api/v1/networks/ethernet/ETHERNET1',
                                    content_type='application/json',
                                    data=json.dumps(test_payload),
                                    headers=headers)
                assert resp.status_code == 200
                payload = load_json(resp)
                assert payload == EXPECTED_ETHERNET1_DISCONNECTED


def test_patch_ethernet_static_invalids(client, headers):
    test_payload = dict(
        configuration=dict(
            dhcp_enabled=False,
            network=dict(
                ipaddr='x',
                netmask='y',
                dns='8.8.8.8, localhost'
            )
        )
    )
    with mock.patch('local_api.apiv1.utils.run_command',
                    side_effect=[DISCONNECTED_UCI_STATE]):
            resp = client.patch('/api/v1/networks/ethernet/ETHERNET1',
                                content_type='application/json',
                                data=json.dumps(test_payload),
                                headers=headers)
            assert resp.status_code == 422
            payload = load_json(resp)
            errors = payload['errors']
            assert 'dns' in errors
            assert 'ipaddr' in errors
            assert 'netmask' in errors
            assert 'gateway' not in errors


def test_get_software(client, headers):
    resp = client.get('/api/v1/system/software',
                      headers=headers)
    assert resp.status_code == 200
    payload = load_json(resp)
    assert 'os' in payload
    assert 'firmware' in payload
    assert 'packages' in payload


@pytest.mark.skipif(sys.platform == 'darwin',
                    reason="psutil sensors_temperatures unavailable on mac")
def test_get_diagnostics(client, headers):
    expected_temp = 39.2
    with mock.patch('local_api.apiv1.utils.run_command',
                    side_effect=[CONNECTED_CLIENTS_SIDE_EFFECT, expected_temp]):
        with mock.patch('local_api.apiv1.soc.read_serial',
                        side_effect=[BAX_SIDE_EFFECT]):
            with mock.patch('local_api.apiv1.utils.psutil.sensors_temperatures',
                            side_effect=[PSUTIL_TEMP_SIDE_EFFECT]):
                resp = client.get('/api/v1/system/diagnostics',
                                headers=headers)
                assert resp.status_code == 200
                payload = load_json(resp)
                assert 'modem' in payload
                assert 'clients' in payload
                assert 'battery' in payload
                assert 'cpu' in payload
                assert payload['modem']['temperature'] == [expected_temp]
                assert payload['battery']['temperature'] == EXPECTED_BAT_TEMPERATURE
                assert payload['cpu']['temperature'] == EXPECTED_CPU_TEMPERATURE
                assert payload['clients'][0] == CONNECTED_CLIENT_PARSED


def test_change_password(client, headers):
    # TODO investigate why this test kills tests following it (fixtures not cleaned up).
    new_password = 'freshpassword'
    test_payload = dict(
        current_password=TEST_PASSWORD,
        password=new_password,
        password_confirmation=new_password
    )
    resp = client.patch('/api/v1/auth/password',
                        data=json.dumps(test_payload),
                        content_type='application/json',
                        headers=headers)
    assert resp.status_code == 200
    assert models.check_password(TEST_USER, new_password)
