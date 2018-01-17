# -*- coding: utf-8 -*-

"""
Utilities for interacting with the filesystem.
"""

import os


def get_storage_status(mount_point='/storage/data'):
    """Returns the disk storage status of a BRCK device in bytes.

    The default mountpoint `/storage/data`.

    Assumes that everything is mounted under /
    :ret dict
    """
    stats = os.statvfs(path)
    state = dict(
        total_space=stats.f_blocks * stats.f_frsize,
        used_space=(stats.f_blocks - stats.f_bfree) * stats.f_frsize,
        available_space=stats.f_bavail * stats.f_frsize
    )
    return state