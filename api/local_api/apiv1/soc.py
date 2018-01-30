# -*- coding: utf-8 -*-

import os
import serial

"""
{'AlarmPwrOnHour': 6,
 'AlarmPwrOnMinute': 0,
 'DelayOffTimerMinutes': 0,
 'DelayedOffTimerEnable': 0,
 'IsAutoStart': 1,
 'PowerOffHour': 20,
 'PowerOffMinute': 1,
 'RetailMode': 0,
 'SocPwrOffLevel': 5,
 'SocPwrOnLevel': 15}

"""

LOG = __import__('logging').getLogger()
DEVICE = '/dev/ttyACM0'
TIMEOUT = 3


def read_serial():
    """Read SOC configuration via serial

    :return: string
    """
    response = []
    if os.path.exists(DEVICE):
        port = serial.Serial(DEVICE, timeout=TIMEOUT)
        loop = True
        port.write('RDC')
        while loop:
            line = port.readline()
            if line:
                response.append(line.decode())
            else:
                loop = False
        port.close()
    else:
        LOG.error("Port does not exist found at: %s", DEVICE)
    return ''.join(response)


def get_soc_settings():
    """Gets SOC settings in API-format

    :return: dict
    """
    soc_settings = {}
    try:
        resp = read_serial()
        parsed = eval(''.join(resp))
        soc_settings['on_time'] = '{d[AlarmPwrOnHour]:02d}:{d[AlarmPwrOnMinute]:02d}'.format(d=parsed)
        soc_settings['off_time'] = '{d[PowerOffHour]:02d}:{d[PowerOffMinute]:02d}'.format(d=parsed)
        soc_settings['soc_on'] = parsed['SocPwrOnLevel']
        soc_settings['soc_off'] = parsed['SocPwrOffLevel']
    except SyntaxError as e:
        LOG.error("Failed to parse SOC settings. Syntax error: %r", e)
    except Exception as e:
        LOG.error("Failed to parse SOC settings. Other error: %r", e)
    return soc_settings


def set_soc_setting(payload):
    """Configures SOC Settings
    """
    pass