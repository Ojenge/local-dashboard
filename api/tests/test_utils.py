# -*- coding: utf-8 -*-

import pytest
import mock

from local_api.apiv1 import utils


def test_get_signal_strength():
    assert utils.get_signal_strength() == 0
    with mock.patch('local_api.apiv1.utils.run_command',
              side_effect=['99', '0', '1', '30', '31']):
              assert utils.get_signal_strength() == 0
              assert utils.get_signal_strength() == 0
              assert utils.get_signal_strength() == 3
              assert utils.get_signal_strength() == 97
              assert utils.get_signal_strength() == 100


