# -*- coding: utf-8 -*-

import json
import pytest

import local_api


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
    assert 'storage' in payload
    storage_payload = payload['storage']
    for k in ['total_space', 'used_space', 'available_space']:
        v = storage_payload.get(k)
        assert v is not None and isinstance(v, int)