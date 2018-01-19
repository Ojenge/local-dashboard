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
    with mock.patch('local_api.apiv1.utils.run_command', return_value=True):
        with mock.patch('local_api.apiv1.utils.read_file', side_effect=['CHARGING', '98']):
            resp = client.get('/api/v1/system')
            assert(resp.status_code == 200)
            payload = load_json(resp)
            assert 'storage' in payload
            assert payload['battery'] == dict(state='CHARGING', battery_level=98)