# -*- coding: utf-8 -*-

"""SIM switching integration
"""

import re
import time
from subprocess import call

from brck.utils import run_command
from brck.utils import is_service_running

from .utils import read_file


LOG = __import__('logging').getLogger()

THREEG_MONITOR_SERVICE = '3g-monitor'
REG_OK = re.compile('^.*OK.*$')
REG_ERROR = re.compile('^.*ERROR.*$')
MODEM1_PATTERN = re.compile(r'.*(/1\-2\.2/).*')
MODEM2_PATTERN = re.compile(r'.*(/1\-2\.3/).*')

SIM_FLAGS = {
    '1-1': [0, 0, 1],
    '1-2': [1, 0, 1],
    '1-3': [1, 1, 1],
    '2-1': [1, 0, 1],
    '2-2': [0, 0, 1],
    '2-3': [0, 1, 1]
}

SIM_STATUS_PATHS = [
    '/sys/class/gpio/gpio339/value',
    '/sys/class/gpio/gpio340/value',
    '/sys/class/gpio/gpio341/value'
]

SIM_CONFIG_PATHS = [
    '/sys/class/gpio/gpio342/value',
    '/sys/class/gpio/gpio344/value',
    '/sys/class/gpio/gpio345/value'
]
MODEM_FLAG_PATHS = [
    '/sys/class/gpio/gpio366/value',
    '/sys/class/gpio/gpio367/value',
    '/sys/class/gpio/gpio368/value'
]


def setup_logging():
    import logging
    LOG.addHandler(logging.StreamHandler())


def stop_service(name):
    run_command(['/etc/init.d/{}'.format(name), 'stop'])


def run_call(path, value):
    command = 'echo {} > {}'.format(value, path)
    LOG.debug('Running: %s', command)
    call(command, shell=True)


def get_modems():
    """Gets active modem set
    :return: (bool, bool)
    """
    m1 = False
    m2 = False
    _path = '/sys/class/tty'
    _paths_str = run_command(['ls', '-l', _path], output=True)
    _paths = _paths_str.splitlines()
    matches1 = [p for p in _paths
                if MODEM1_PATTERN.match(p)]
    matches2 = [p for p in _paths
                if MODEM2_PATTERN.match(p)]
    if len(matches1) == 4:
        m1 = True
    if len(matches2) == 4:
        m2 = True
    return (m1, m2)


def sim_exists(sim_id):
    """Checks existence of SIM
    """
    assert isinstance(sim_id, int)
    assert (sim_id >= 1 and sim_id <= 3)
    exists = False
    flag_path = SIM_STATUS_PATHS[sim_id - 1]
    flag = read_file(flag_path)
    exists = flag == '1'
    if flag == False:
        LOG.error('Failed to read sim status at: %s', flag_path)
    return exists


def connect_sim(sim_id, pin='', puk=''):
    """Attempts to establish a connect to the with this SIM
    """
    errors = {}
    sim_no = int(sim_id[-1])
    if is_service_running(THREEG_MONITOR_SERVICE):
        stop_service(THREEG_MONITOR_SERVICE)
    m1, m2 = get_modems()
    modem = 0
    if m1:
        modem = 1
    elif m2:
        modem = 2
    if modem:
        key = '%d-%d' % (modem, sim_no)
        flags = SIM_FLAGS.get(key)
        if flags:
            run_command(['ifdown', 'wan'])
            for (key, flag) in enumerate(flags):
                port_path = SIM_CONFIG_PATHS[key]
                run_call(port_path, flag)
            for modem_flag_path in MODEM_FLAG_PATHS:
                run_call(modem_flag_path, '0')
                time.sleep(1)
                run_call(modem_flag_path, '1')
            time.sleep(5)
            if pin:
                pin_resp = run_command(['querymodem', 'set_pin', 'puk', 'pin'],
                                        output=True)
                if REG_ERROR.match(pin_resp):
                    errors['pin'] = 'PIN/PUK error'
            if not errors:
                time.sleep(3)
                carrier_resp = run_command(['querymodem', 'carrier'], output=True)
                if REG_ERROR.match(carrier_resp):
                    errors['network'] = 'Failed to connect to network'
            run_command(['ifdown', 'wan'])
            run_command(['ifup', 'wan'])
        else:
            LOG.error("uknown modem configuration")
    else:
        errors['network'] = 'no modem found'
    return errors
