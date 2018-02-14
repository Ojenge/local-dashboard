# -*- coding: utf-8 -*-

import mock
import pytest
from copy import copy

from local_api.apiv1 import utils
from local_api.apiv1 import soc

DUMMY_SOC_RESPONSE = """{"SocPwrOnLevel":15,"SocPwrOffLevel":5,"AlarmPwrOnHour":06,"AlarmPwrOnMinute":00,
"PowerOffHour":20,"PowerOffMinute":01,"IsAutoStart":1,"DelayedOffTimerEnable":0,"DelayOffTimerMinutes":0,"RetailMode":0}
"""
EXPECTED_SOC_SETTINGS = {
    'soc_on': 15,
    'soc_off': 5,
    'on_time': '06:00',
    'off_time': '20:01',
    'delay_off': 0,
    'delay_off_minutes': 0,
    'retail': 0,
    'auto_start': 1
}

DUMMY_VERSION_RESPONSE = u'{"Firmware Version": 1.0.1-carp,"Build": "Oct 23 2017 13:37:04"}'
EXPECTED_VERSION = '1.0.1-carp : Oct 23 2017 13:37:04'

NORMAL_SOC_SETTINGS = dict(mode='NORMAL', soc_on=10, soc_off=5)
SOC_SCENARIOS = [
    (dict(mode='NORMAL', soc_on=10, soc_off=5), True,
     dict(mode='NORMAL', soc_on=10, soc_off=5, retail=1)),

     (dict(mode='TIMED'), False, True),

     (dict(mode='ALWAYS_ON'), True, dict(mode='ALWAYS_ON', auto_start=1)),

     (dict(mode='ALWAYS_ON', soc_on=10, soc_off=2), True,

      dict(mode='ALWAYS_ON', soc_on=10, soc_off=2, auto_start=1)),

     (dict(mode='VEHICLE'), True,
      dict(mode='VEHICLE', auto_start=0)),

     (dict(mode='VEHICLE', delay_off_minutes=10), True,
      dict(mode='VEHICLE', delay_off_minutes=10, delay_off=1, auto_start=0)),

     (dict(mode='MANUAL'), True, True),

     (dict(mode='MANUAL', delay_off_minutes=1), True,
      dict(mode='MANUAL', delay_off=1, delay_off_minutes=1, auto_start=0)),

     (dict(mode='MANUAL', delay_off_minutes=0), False, True),

     (dict(mode='MANUAL', delay_off_minutes=120), False, True),
]


def test_get_signal_strength():
    assert utils.get_signal_strength('wan') == 0
    assert utils.get_signal_strength('lan') == 100
    with mock.patch('local_api.apiv1.utils.run_command',
                    side_effect=['99', '0', '1', '30', '31']):
        assert utils.get_signal_strength('wan') == 0
        assert utils.get_signal_strength('wan') == 0
        assert utils.get_signal_strength('wan') == 3
        assert utils.get_signal_strength('wan') == 97
        assert utils.get_signal_strength('wan') == 100


def test_get_soc_settings():
    with mock.patch('local_api.apiv1.soc.read_serial',
                    side_effect=[DUMMY_SOC_RESPONSE]):
        settings = soc.get_soc_settings()
        assert settings == EXPECTED_SOC_SETTINGS


@pytest.mark.parametrize("payload,valid,out", SOC_SCENARIOS)
def test_validate_soc_settings(payload, valid, out):
    orig = copy(payload)
    v, np = soc.validate_payload(payload)
    assert v.is_valid == valid
    if out == True:
        assert np == orig
    else:
        assert np == out


def test_soc_command():
    command = 'WRC15,5,6,0,20,1,1,0,0,0'
    assert soc.payload_to_command(EXPECTED_SOC_SETTINGS) == command


def test_get_firmware_version():
    with mock.patch('local_api.apiv1.soc.read_serial',
                    side_effect=[DUMMY_VERSION_RESPONSE]):
        version = soc.get_firmware_version()
        assert version == EXPECTED_VERSION
