# -*- coding: utf-8 -*-

import os
import mock
import pytest
from copy import copy
from itertools import chain

from local_api.apiv1 import utils
from local_api.apiv1 import soc
from local_api.apiv1 import sim

DUMMY_SOC_RESPONSE = """{
  "DelayedOffTimerEnable": 1,
  "DelayOffTimerMinutes": 120,
  "SocPwrOffLevel": 1,
  "IsAutoStart": 0,
  "AlarmPwrOnHour": 5,
  "SocPwrOnLevel": 15,
  "PowerOffMinute": 0,
  "AlarmPwrOnMinute": 0,
  "PowerOffHour": 22,
  "RetailMode": 1
}
"""
EXPECTED_SOC_SETTINGS = {
    'soc_on': 15,
    'soc_off': 1,
    'on_time': '05:00',
    'off_time': '22:00',
    'delay_off': 1,
    'delay_off_minutes': 120,
    'retail': 1,
    'auto_start': 0
}

DUMMY_VERSION_RESPONSE = u'{"Firmware Version": 1.0.1-carp,"Build": "Oct 23 2017 13:37:04"}'
EXPECTED_FIRMWARE_VERSION = '1.0.1-carp : Oct 23 2017 13:37:04'

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

EXPECTED_PACKAGE_VERSIONS = [
    {'installed': True, 'name': '3g-monitor', 'version': 'v0.0.24-9'},
    {'installed': True, 'name': 'battery-monitor', 'version': 'v0.0.24-9'},
    {'installed': True, 'name': 'connected_clients', 'version': 'v0.0.24-9'},
    {'installed': True, 'name': 'core-services', 'version': 'v0.0.2-rc13-6'},
    {'installed': True, 'name': 'gps-monitor', 'version': 'v0.0.24-9'},
    {'installed': True, 'name': 'moja', 'version': 'v1.0.19-rc32-1'},
    {'installed': True, 'name': 'moja-captive', 'version': 'v1.0.7-rc2-9'},
    {'installed': True, 'name': 'python-brck-sdk', 'version': 'v0.0.1-rc28-3'},
    {'installed': True, 'name': 'querymodem', 'version': 'v0.0.24-9'},
    {'installed': True, 'name': 'scan_wifi', 'version': 'v0.0.24-9'},
    {'installed': True, 'name': 'supabrck-core', 'version': 'v0.11.3-5'}]


def test_get_signal_strength():
    assert utils.get_signal_strength('wan') == 0
    assert utils.get_signal_strength('lan') == 100
    _side_effect = list(chain(*[['ME936', v] for v in ['99', '0', '1', '30', '31', '255', '']]))
    with mock.patch('local_api.apiv1.utils.run_command',
                    side_effect=_side_effect):
        assert utils.get_signal_strength('wan') == 99
        assert utils.get_signal_strength('wan') == 0
        assert utils.get_signal_strength('wan') == 1
        assert utils.get_signal_strength('wan') == 30
        assert utils.get_signal_strength('wan') == 31
        assert utils.get_signal_strength('wan') == 0
        assert utils.get_signal_strength('wan') == 0
    _side_effect = list(chain(*[['MU736', v] for v in ['99', '0', '1', '30', '31', '255', '']]))
    with mock.patch('local_api.apiv1.utils.run_command',
                    side_effect=_side_effect):
        assert utils.get_signal_strength('wan') == 0
        assert utils.get_signal_strength('wan') == 0
        assert utils.get_signal_strength('wan') == 3
        assert utils.get_signal_strength('wan') == 97
        assert utils.get_signal_strength('wan') == 100
        assert utils.get_signal_strength('wan') == 0
        assert utils.get_signal_strength('wan') == 0
    _side_effect = list(chain(*[[None, v] for v in ['99', '0', '1', '30', '31', '255', '']]))
    with mock.patch('local_api.apiv1.utils.run_command',
                    side_effect=_side_effect):
        assert utils.get_signal_strength('wan') == 0
        assert utils.get_signal_strength('wan') == 0
        assert utils.get_signal_strength('wan') == 3
        assert utils.get_signal_strength('wan') == 97
        assert utils.get_signal_strength('wan') == 100
        assert utils.get_signal_strength('wan') == 0
        assert utils.get_signal_strength('wan') == 0


def test_get_soc_settings():
    with mock.patch('local_api.apiv1.soc.run_command',
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
    command = 'WRC15,1,5,0,22,0,0,1,120,1'
    assert soc.payload_to_command(EXPECTED_SOC_SETTINGS) == command


def test_get_firmware_version():
    with mock.patch('local_api.apiv1.soc.run_command',
                    side_effect=[DUMMY_VERSION_RESPONSE]):
        version = soc.get_firmware_version()
        assert version == EXPECTED_FIRMWARE_VERSION


def test_get_software():
    assert utils.get_software()
    expected_os_version = 'LATEST'
    v_file = os.path.join(os.path.dirname(__file__), 'packages-installed.txt')
    with open(v_file) as fd:
         package_version_response = fd.read()
         with mock.patch('local_api.apiv1.utils.get_firmware_version',
                        side_effect=[EXPECTED_FIRMWARE_VERSION]):
            with mock.patch('local_api.apiv1.utils.run_command',
                            side_effect=[expected_os_version, package_version_response]):
                versions = utils.get_software()
                assert versions['os'] == expected_os_version
                assert versions['firmware'] == EXPECTED_FIRMWARE_VERSION
                assert versions['packages'] == EXPECTED_PACKAGE_VERSIONS



def test_get_modem_net_info():
    _xcell_info = '0,2,639,  3,017a,72731,306,10637, 52,  9,255'
    _xcell_info_01 = '0,2,639, 23,017a,72731,306,10637, 52,  9,255'
    expected = dict(
        mnc='  3',
        net_type='UMTS (3G)',
        cell_id=468785,
        lac=378
    )
    expected_01 = dict(
        mnc=' 23',
        net_type='UMTS (3G)',
        cell_id=468785,
        lac=378
    )
    with mock.patch('local_api.apiv1.sim.run_command',
            side_effect=[_xcell_info, _xcell_info_01, '']):
            assert sim.get_modem_network_info() == expected
            assert sim.get_modem_network_info() == expected_01
            assert sim.get_modem_network_info() == {}