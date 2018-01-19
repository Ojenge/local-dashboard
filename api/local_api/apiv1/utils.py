# -*- coding: utf-8 -*-

"""
Utilities for interacting with the filesystem.
"""

import os
from brck.utils import run_command


LOG = __import__('logging').getLogger()

STATE_OK = 'OK'
STATE_ERROR = 'ERROR'
STATE_UNKNOWN = 'UNKNOWN'


def read_file(path):
    contents = False
    try:
        with open(path) as f:
            contents = f.read()
    except IOError:
        LOG.error('Failed to read file at %s', path)
    return contents


def get_storage_status(mount_point='/storage/data'):
    """Gets the disk storage status of a BRCK device in bytes.

    The default mountpoint `/storage/data`.

    Assumes that everything is mounted under /
    :return: dict
    """
    state = dict(
        total_space=0,
        used_space=0,
        available_space=0
    )
    try:
        stats = os.statvfs(mount_point)
        state = dict(
            total_space=stats.f_blocks * stats.f_frsize,
            used_space=(stats.f_blocks - stats.f_bfree) * stats.f_frsize,
            available_space=stats.f_bavail * stats.f_frsize
        )
    except OSError:
        LOG.error('Failed to get storage status for mountpoint at: %s', mount_point)
    return state


def get_battery_status():
    """Gets the battery status of the BRCK device.

        Sample Response:
        {
            'state': 'CHARGING',
            'battery_level': 98
        }

    :return: dict
    """
    battery_level = 0
    state = 'UNKNOWN'
    check_resp = run_command('check_battery', output=False)
    if check_resp:
        state = read_file('/tmp/battery/status') or STATE_UNKNOWN
        capacity = read_file('/tmp/battery/capacity')
        try:
            battery_level = int(capacity)
        except ValueError:
            LOG.error('Failed to ready battery capacity | Returned: %s', capacity)
    state = dict(
        state=state.upper(),
        battery_level=battery_level
    )
    return state
