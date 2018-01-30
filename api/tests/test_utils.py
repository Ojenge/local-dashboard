# -*- coding: utf-8 -*-

import mock

from local_api.apiv1 import utils
from local_api.apiv1 import soc

DUMMY_SOC_RESPONSE = """{"SocPwrOnLevel":15,"SocPwrOffLevel":5,"AlarmPwrOnHour":06,"AlarmPwrOnMinute":00,
"PowerOffHour":20,"PowerOffMinute":01,"IsAutoStart":1,"DelayedOffTimerEnable":0,"DelayOffTimerMinutes":0,"RetailMode":0}
"""
EXPECTED_SOC_SETTINGS = {
    'soc_on': 15,
    'soc_off': 5,
    'on_time': '06:00',
    'off_time': '20:01'
}


def test_get_signal_strength():
    assert utils.get_signal_strength() == 0
    with mock.patch('local_api.apiv1.utils.run_command',
                    side_effect=['99', '0', '1', '30', '31']):
        assert utils.get_signal_strength() == 0
        assert utils.get_signal_strength() == 0
        assert utils.get_signal_strength() == 3
        assert utils.get_signal_strength() == 97
        assert utils.get_signal_strength() == 100


def test_get_soc_settings():
    with mock.patch('local_api.apiv1.soc.read_serial',
                    side_effect=[DUMMY_SOC_RESPONSE]):
        settings = soc.get_soc_settings()
        assert settings == EXPECTED_SOC_SETTINGS


def test_soc_command():
    command = 'WRC15,5,6,0,20,1,0'
    assert soc.payload_to_command(EXPECTED_SOC_SETTINGS) == command