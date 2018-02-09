# -*- coding: utf-8 -*-

import os
import serial
import re
from datetime import datetime

from brck.utils import uci_set
from brck.utils import uci_get
from brck.utils import uci_commit

from .schema import Validator
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
REGEX_TIME = re.compile('^(0[0-9]|1[0-9]|2[0-3]):(0[0-9]|[1-5][0-9])$')

MODE_NORMAL = 'NORMAL'
MODE_TIMED = 'TIMED'
MODE_ALWAYS_ON = 'ALWAYS_ON'
MODE_VEHICLE = 'VEHICLE'
MODE_MANUAL = 'MANUAL'
MODES = [MODE_NORMAL, MODE_TIMED, MODE_ALWAYS_ON, MODE_VEHICLE, MODE_MANUAL]
MODE_DEFAULTS = {
    MODE_NORMAL: { 'retail': 1 },
    MODE_ALWAYS_ON: {'auto_start': 1},
    MODE_VEHICLE: { 'auto_start': 0, 'delay_off': 1},
    MODE_TIMED: { 'auto_start': 0 }
}


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



def validate_payload(payload):
    """Validates soc settings payload for persistence.
    """
    assert isinstance(payload, dict)
    validator = Validator(payload)
    validator.ensure_inclusion('mode', MODES)
    mode = payload.get('mode', '')
    has_soc = 'soc_on' in payload or 'soc_off' in payload
    has_time = 'on_time' in payload or 'off_time' in payload
    if has_soc:
        validator.required_together('soc_on', 'soc_off')
        validator.ensure_range('soc_on', 1, 99, int)
        validator.ensure_range('soc_off', 1, 99, int)
        validator.ensure_less_than('soc_off', 'soc_on')
    if has_time or (mode in [MODE_TIMED]):
        validator.required_together('on_time', 'off_time')
        validator.ensure_format('on_time', REGEX_TIME)
        validator.ensure_format('off_time', REGEX_TIME)
        validator.ensure_not_equal('on_time', 'off_time')
    if mode == MODE_MANUAL:
        validator.ensure_inclusion('auto_start', [0, 1], required=False)
        validator.ensure_inclusion('delay_off', [0, 1], required=False)
        if 'delay_off' in payload:
            validator.ensure_exact('auto_start', 0)
            validator.required_together('delay_off', 'delay_off_minutes')
            validator.ensure_range('delay_off_minutes', 1, 60)
        validator.ensure_inclusion('retail', [0, 1], required=False)
    else:
        validator.ensure_excluded('auto_start', 'delay_off', 'retail')
    if validator.is_valid:
        # push in defaults
        payload.update(MODE_DEFAULTS.get(mode, {}))
    return (validator, payload)

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


def configure_power(payload):
    """Validate and configure SOC configuration
    """
    validator, payload_actual = validate_payload(payload)
    if validator.is_valid:
        uci_set('brck.power', 'power')
        uci_set('brck.power.mode', payload_actual['mode'])
        uci_commit('brck.power')
        command = payload_to_command(payload_actual)
        status = set_soc(command)
        if status:
            return (200, 'OK')
        else:
            return (422, {'soc': 'Command Error'})
    else:
        return (422, validator.errors)


def get_power_config():
    """Gets the current power configuraition of the device
    """
    configured = False
    mode = uci_get('brck.power.mode')
    if mode != False:
        configured = True
    else:
        mode = None
    return dict(
        configured=configured,
        mode=mode
    )