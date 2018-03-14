# -*- coding: utf-8 -*-

"""SIM switching integration
"""

import re
from subprocess import call

import eventlet

from brck.utils import (
    run_command,
    is_service_running,
    uci_get,
    uci_set,
    uci_delete,
    uci_commit
)

from .utils import read_file, get_uci_state


LOG = __import__('logging').getLogger()

THREEG_MONITOR_SERVICE = '3g-monitor'
REG_OK = re.compile('^.*OK.*$', re.MULTILINE)
REG_ERROR = re.compile('^.*ERROR.*$', re.MULTILINE)
REG_READY = re.compile('^READY.*$')
REG_PIN = re.compile('^.*PIN.*$')
REG_PUK = re.compile('^.*PUK.*$')
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

# Connection states
NO_MODEM = 'NO_MODEM'
DISABLE_3G_MONITOR = 'DISABLE_3G_MONITOR'
STOP_WAN = 'STOP_WAN'
SELECT_SIM = 'SELECTING_SIM'
CHECK_SIM = 'CHECK_SIM'
SIM_DETECTED = 'SIM_DETECTED'
CHECK_PIN = 'CHECK_PIN'
CHECK_READY = 'CHECK_READY'
REQUIRES_APN = 'REQUIRES_APN'
REQUIRES_PIN = 'REQUIRES_PIN'
REQUIRES_PUK = 'REQUIRES_PUK'
SET_PIN = 'SET_PIN'
SET_PUK = 'SET_PUK'
PIN_OK = 'PIN_OK'
PUK_OK = 'PUK_OK'
PIN_REJECTED = 'PIN_REJECTED'
PUK_REJECTED = 'PUK_REJECTED'
DELETE_PIN = 'DELETE_PIN'
DELETE_PUK = 'DELETE_PUK'
PIN_NOT_REQUIRED = 'PIN_NOT_REQUIRED'
SIM_READY = 'SIM_READY'
SIM_NOT_READY = 'SIM_NOT_READY'
ACTIVE_SIM_RESET = 'ACTIVE_SIM_RESET'
DISABLE_PIN = 'DISABLE_PIN'
CHECK_CARRIER = 'CHECK_CARRIER'
WAIT_CARRIER = 'WAIT_CARRIER'
NO_CARRIER = 'NO_CARRIER'
CARRIER_DETECTED = 'CARRIER_DETECTED'
RESTART_MODEM = 'RESTART_MODEM'
START_WAN = 'START_WAN'
WAIT_CONNECTION = 'WAIT_CONNECTION'
CONNECTED = 'CONNECTED'
NO_CONNECTION = 'NO_CONNECTION'
ENABLE_3G_MONITOR = 'ENABLE_3G_MONITOR'
CONN_STATES_VERBOSE = {
    NO_MODEM: 'No modem detected',
    DISABLE_3G_MONITOR: 'Disabling 3G monitor temporarily',
    STOP_WAN: 'Bringing down WAN interface',
    SELECT_SIM: 'Selecting SIM',
    CHECK_SIM: 'Checking SIM',
    SIM_DETECTED: 'SIM detected',
    CHECK_PIN: 'Checking if PIN is required',
    CHECK_READY: 'Checking if the SIM is ready',
    REQUIRES_PIN: 'This SIM requires a PIN to connect',
    REQUIRES_PUK: 'This SIM is blocked.',
    REQUIRES_APN: 'This SIM requires an APN to connect',
    SET_PIN: 'Setting PIN',
    SET_PUK: 'Setting PUK',
    PIN_REJECTED: 'PIN rejected',
    PUK_REJECTED: 'PUK rejected',
    PIN_OK: 'PIN accepted',
    PUK_OK: 'PUK accepted',
    DISABLE_PIN: 'Disabling the PIN lock',
    DELETE_PIN: 'Deleting saved PIN',
    DELETE_PUK: 'Deleting saved PUK',
    PIN_NOT_REQUIRED: 'PIN not required',
    SIM_READY: 'SIM is ready',
    SIM_NOT_READY: 'SIM not ready - giving up',
    ACTIVE_SIM_RESET: 'Restoring previous active SIM configuration',
    CHECK_CARRIER: 'Checking Carrier',
    WAIT_CARRIER: 'Waiting for carrier detection',
    NO_CARRIER: 'No carrier detected - giving up',
    CARRIER_DETECTED: 'Carrier detected',
    RESTART_MODEM: 'Restarting the modem',
    START_WAN: 'Bringing up WAN interface',
    WAIT_CONNECTION: 'Waiting for connection (60s)',
    CONNECTED: 'Connected!',
    NO_CONNECTION: 'No connection',
    ENABLE_3G_MONITOR: 'Restarting 3G monitor'
}


DEFAULT_PIN = '0000'

def enable_service(name):
    run_command(['/etc/init.d/{}'.format(name), 'enable'])


def disable_service(name):
    run_command(['/etc/init.d/{}'.format(name), 'disable'])


def stop_service(name):
    run_command(['/etc/init.d/{}'.format(name), 'stop'])


def start_service(name):
    run_command(['/etc/init.d/{}'.format(name), 'start'])


def run_call(path, value):
    command = 'echo {} > {}'.format(value, path)
    LOG.debug('Running: %s', command)
    call(command, shell=True)


def get_connection_status():
    """Gets the connection status via 3g-wan interface

    :return bool:
    """
    command = ['ping', '-c', '2', '-I', '3g-wan', '-W', '1', '8.8.8.8']
    return run_command(command)

def get_sim_state(sim_id):
    """Gets SIM state as stored in UCI
    :return: dict
    """
    assert sim_id in [1, 2, 3]
    sim_state = {}
    state_path = 'brck.sim%d' % sim_id
    state = get_uci_state(state_path)
    if state:
        sim_state['active'] = state.get('brck.sim%d.active' % sim_id) == '1'
        sim_state['apn'] = state.get('brck.sim%d.apn' % sim_id)
        sim_state['username'] = state.get('brck.sim%d.username' % sim_id)
        sim_state['password'] = state.get('brck.sim%d.password' % sim_id)
    return sim_state


def set_sim_state(sim_id, pin=None, puk=None, apn=None, username=None, password=None, active=False):
    assert sim_id in [1, 2, 3]
    _params = dict(pin=pin,
                   puk=puk,
                   apn=apn,
                   username=username,
                   password=password,
                   active=int(active))
    change_count = 0
    state_path = 'brck.sim%d' % sim_id
    if not uci_get(state_path):
        LOG.debug("Initializing SIM section in uci: %s", state_path)
        uci_set(state_path, 'sims')
        uci_commit(state_path)
    for name, value in _params.iteritems():
        if value:
            _path = 'brck.sim%d.%s' % (sim_id, name)
            LOG.debug("Setting UCI value: %s | %r", _path, value)
            uci_set(_path, str(value))
            change_count += 1
    # configure active_sim
    if active:
        uci_set('brck.active_sim', str(sim_id))
        if apn:
            uci_set('network.wan.apn', apn)
            change_count += 1
        if username:
            uci_set('network.wan.username', username)
            change_count += 1
        if password:
            uci_set('network.wan.password', password)
            change_count += 1
        change_count += 1
    if change_count > 0:
        uci_commit('brck')
        uci_commit('network.wan')


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


def restart_modem():
    """Restarts the current modem
    """
    LOG.warn("Restarting modem")
    s0 = run_command(['querymodem', 'AT+CFUN=4'])
    s1 = run_command(['querymodem', 'AT+CFUN=6'])
    LOG.warn("Restart modem status|%r|%r", s0, s1)


def disable_pin(pin):
    """Disable PIN
    """
    s0 = run_command(['querymodem', "AT+CLCK=SC,0,{}".format(pin)])
    LOG.warn("Disable PIN status|%r", s0)


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


def emit_event(io, event, namespace):
    """Emits event to websocket
    """
    description = CONN_STATES_VERBOSE.get(event, event)
    payload = {'event': event,
               'description': description}
    LOG.warn('Sending websocket event: %r', payload)
    io.emit('conn_event', payload, namespace=namespace)


def connect_sim_actual(sim_id, modem_id, previous_sim):
    """Connects to the selected SIM in interactive fashion.

    This method pushes all events to a websocket topic for consumption.

    :param int sim_id: SIM ID (1 or 2 or 3)
    :param int modem_Id: Modem ID (1 or 2)
    """
    from local_api import socketio as io, NS_SIM_CONNECTIVITY as ns
    if is_service_running(THREEG_MONITOR_SERVICE):
        LOG.warn("Stopping 3g-monitor")
        disable_service(THREEG_MONITOR_SERVICE)
        stop_service(THREEG_MONITOR_SERVICE)
        emit_event(io, DISABLE_3G_MONITOR, ns)
    else:
        LOG.warn("3g-monitor is already stopped")
    flags = SIM_FLAGS.get('%d-%d' % (modem_id, sim_id))
    if flags:
        LOG.warn("Bringing down WAN")
        run_command(['ifdown', 'wan'])
        emit_event(io, STOP_WAN, ns)
        emit_event(io, SELECT_SIM, ns)
        for (key, flag) in enumerate(flags):
            port_path = SIM_CONFIG_PATHS[key]
            run_call(port_path, flag)
        for modem_flag_path in MODEM_FLAG_PATHS:
            run_call(modem_flag_path, '0')
            eventlet.sleep(1)
            run_call(modem_flag_path, '1')
        eventlet.sleep(5)
        emit_event(io, CHECK_SIM, ns)
        check_imei_status = run_command(['querymodem', 'imei'], output=True)
        LOG.warn("SIM|IMEI STATUS|%s", check_imei_status)
        requires_input = False
        if not REG_ERROR.match(check_imei_status):
            emit_event(io, SIM_DETECTED, ns)
            emit_event(io, CHECK_PIN, ns)
            pin_status = run_command(['querymodem', 'check_pin'], output=True)
            LOG.warn("SIM|PIN STATUS|%s", pin_status)
            puk_path = 'brck.sim{}.puk'.format(sim_id)
            pin_path = 'brck.sim{}.pin'.format(sim_id)
            ready = False
            if REG_PUK.match(pin_status):
                puk = uci_get(puk_path)
                pin = uci_get(pin_path)
                if puk:
                    emit_event(io, SET_PUK, ns)
                    pin = pin or DEFAULT_PIN
                    set_puk_status = run_command(['querymodem', 'AT+CPIN={},{}'.format(puk, pin)], output=True)
                    LOG.warn("SIM|SET PUK STATUS|%s", set_puk_status)
                    if not REG_ERROR.match(set_puk_status):
                        emit_event(io, DISABLE_PIN, ns)
                        disable_pin(pin)
                        eventlet.sleep(3)
                        emit_event(io, PUK_OK, ns)
                        emit_event(io, CHECK_READY, ns)
                        eventlet.sleep(5)
                        check_sim_ready_status = run_command(['querymodem', 'check_pin'], output=True)
                        if REG_READY.match(check_sim_ready_status):
                            emit_event(io, SIM_READY, ns)
                            ready = True
                        else:
                            emit_event(io, DELETE_PUK, ns)
                            uci_delete(puk_path)
                            uci_commit('brck')
                            emit_event(io, SIM_NOT_READY, ns)
                    else:
                        emit_event(io, PUK_REJECTED, ns)
                        emit_event(io, DELETE_PUK, ns)
                        uci_delete(puk_path)
                        uci_commit('brck')
                        emit_event(io, REQUIRES_PUK, ns)
                        requires_input = True
                else:
                    emit_event(io, REQUIRES_PUK, ns)
                    requires_input = True
            elif REG_PIN.match(pin_status):
                pin = uci_get(pin_path)
                if pin:
                    emit_event(io, SET_PIN, ns)
                    set_pin_status = run_command(['querymodem', 'AT+CPIN={}'.format(pin)], output=True)
                    LOG.warn("SIM|SET PIN STATUS|%s", set_pin_status)
                    if not REG_ERROR.match(set_pin_status):
                        emit_event(io, PIN_OK, ns)
                        emit_event(io, DISABLE_PIN, ns)
                        disable_pin(pin)
                        emit_event(io, CHECK_READY, ns)
                        eventlet.sleep(5)
                        check_sim_ready_status = run_command(['querymodem', 'check_pin'], output=True)
                        if REG_READY.match(check_sim_ready_status):
                            emit_event(io, SIM_READY, ns)
                            ready = True
                        else:
                            emit_event(io, DELETE_PIN, ns)
                            uci_delete(pin_path)
                            uci_commit('brck')
                            emit_event(io, SIM_NOT_READY, ns)
                    else:
                        emit_event(io, PIN_REJECTED, ns)
                        emit_event(io, DELETE_PIN, ns)
                        uci_delete(pin_path)
                        uci_commit('brck')
                        emit_event(io, REQUIRES_PIN, ns)
                        requires_input = True
                else:
                    emit_event(io, REQUIRES_PIN, ns)
                    requires_input = True
            elif REG_READY.match(pin_status):
                emit_event(io, PIN_NOT_REQUIRED, ns)
                ready = True
            else:
                emit_event(io, SIM_NOT_READY, ns)
                if previous_sim in ['1', '2', '3']:
                    uci_set('brck.active_sim', previous_sim)
                    uci_commit('brck')
                else:
                    uci_delete('brck.active_sim')
                uci_commit('brck')
                emit_event(io, ACTIVE_SIM_RESET, ns)
            if ready:
                if uci_get('network.wan.apn'):
                    emit_event(io, WAIT_CARRIER, ns)
                    eventlet.sleep(10)
                    emit_event(io, CHECK_CARRIER, ns)
                    carrier_resp = run_command(['querymodem', 'carrier'], output=True)
                    LOG.warn("SIM|CHECK CARRIER STATUS|%s", carrier_resp)
                    if REG_ERROR.match(carrier_resp) or carrier_resp == "0":
                        emit_event(io, NO_CARRIER, ns)
                        # emit_event(io, RESTART_MODEM, ns)
                        # restart_modem()
                        # eventlet.sleep(10)
                    else:
                        emit_event(io, CARRIER_DETECTED, ns)
                        emit_event(io, START_WAN, ns)
                        LOG.warn("Bringing up WAN")
                        run_command(['ifup', 'wan'])
                        emit_event(io, WAIT_CONNECTION, ns)
                        _connected = False
                        for _ in xrange(6):
                            _connected = get_connection_status()
                            if _connected:
                                emit_event(io, CONNECTED, ns)
                                break
                            else:
                                eventlet.sleep(10)
                        if not _connected:
                            emit_event(io, NO_CONNECTION, ns)
                else:
                    emit_event(io, REQUIRES_APN, ns)
                    requires_input = True
        else:
            emit_event(io, SIM_NOT_READY, ns)
    else:
        LOG.error('No such modem configuration exists: SIM: %d MODEM: %d', sim_id, modem_id)
        emit_event(io, NO_MODEM, ns)
    if not requires_input:
        LOG.warn("Bringing up WAN")
        run_command(['ifup', 'wan'])
        emit_event(io, ENABLE_3G_MONITOR, ns)
        LOG.warn('Enabling 3G Monitor')
        enable_service(THREEG_MONITOR_SERVICE)
        start_service(THREEG_MONITOR_SERVICE)


def connect_sim(sim_id, pin='', puk='', apn='', username='', password=''):
    """Attempts to establish a connect to the with this SIM
    """
    previous_sim = uci_get('brck.active_sim')
    errors = {}
    sim_id = int(sim_id[-1])
    m1, m2 = get_modems()
    modem = 0
    if m1:
        modem = 1
    elif m2:
        modem = 2
    if modem:
        LOG.warn('Saving SIM STATE')
        set_sim_state(sim_id,
                      pin=pin,
                      puk=puk,
                      apn=apn,
                      username=username,
                      password=password,
                      active=True)
        eventlet.call_after_global(1, connect_sim_actual, sim_id, modem, previous_sim)
    else:
        errors['network'] = 'no modem found'
    return errors
