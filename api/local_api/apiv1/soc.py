# -*- coding: utf-8 -*-

import os
import serial
import re
from datetime import datetime

from .cache import cached

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
TIME_FORMAT = '%H:%M'
CONFIG_PATTERN = re.compile("\w+\:\d+")

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
    _resp = ''.join(response)
    _final = _resp.replace('\n', '')
    return _final


def parse_serial(raw_content):
    """Parses Serial Response into a dictionary
    :return: dict
    """
    _stripped = raw_content.replace('"', '')
    configs = CONFIG_PATTERN.findall(_stripped)
    tuples = [c.split(":") for c in configs]
    return dict([(k, int(v)) for k,v in tuples])


@cached(timeout=(60 * 10))
def get_soc_settings():
    """Gets SOC settings in API-compatible format.

    :return: dict
    """
    soc_settings = {}
    try:
        resp = read_serial()
        parsed = parse_serial(resp)
        soc_settings['on_time'] = '{d[AlarmPwrOnHour]:02d}:{d[AlarmPwrOnMinute]:02d}'.format(d=parsed)
        soc_settings['off_time'] = '{d[PowerOffHour]:02d}:{d[PowerOffMinute]:02d}'.format(d=parsed)
        soc_settings['soc_on'] = parsed['SocPwrOnLevel']
        soc_settings['soc_off'] = parsed['SocPwrOffLevel']
        soc_settings['delay_off'] = parsed['DelayedOffTimerEnable']
        soc_settings['delay_off_minutes'] = parsed['DelayOffTimerMinutes']
        soc_settings['retail'] = parsed['RetailMode']
    except SyntaxError as e:
        LOG.error("Failed to parse SOC settings. Syntax error: %r", e)
    except Exception as e:
        LOG.error("Failed to parse SOC settings. Other error: %r", e)
    return soc_settings



def payload_to_command(payload):
    """Converts API payload to serial command
    """
    soc_on = payload['soc_on']
    soc_off = payload['soc_off']
    on_date = datetime.strptime(payload['on_time'], TIME_FORMAT)
    off_date = datetime.strptime(payload['off_time'], TIME_FORMAT)
    auto_start = payload.get('auto_start', 0)
    delay_off = payload.get('delay_off', 0)
    delay_off_minutes = payload.get('delay_off_minutes', 0)
    retail = payload.get('retail', 0)
    command = 'WRC%d,%d,%d,%d,%d,%d,%d,%d,%d,%d' % (soc_on, soc_off,
                                           on_date.hour, on_date.minute,
                                           off_date.hour, off_date.minute,
                                           auto_start, delay_off,
                                           delay_off_minutes,
                                           retail)
    return command


def set_soc(payload):
    """Configures SOC Settings

    :return: bool
    """
    command = payload_to_command(payload)
    status = False
    port = None
    try:        
        port = serial.Serial(DEVICE, timeout=TIMEOUT)
        port.write(command)
        status = True
    except serial.serialutil.SerialException as exc:
        LOG.error("Failed to connect to serial port: %r", exc)
    except Exception as exc:
        LOG.error("Failed to write port configuration with error: %r", exc)
    finally:
        if isinstance(port, serial.Serial):
            port.close()
    return status
