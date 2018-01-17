# -*- coding: utf-8 -*-

"""
Utilities for interacting with the filesystem.
"""

import os


def get_storage_status(path='/'):
    """Returns the disk storage status of a BRCK device in bytes.

    Assumes that everything is mounted under /
    :ret dict
    """
    stats = os.statvfs(path)
    state = dict(
        total_space = stats.f_blocks * stats.f_bsize,
        used_space = stats.f_bfree * stats.f_frsize,
        available_space = stats.f_bavail * stats.f_bsize
    )
    return state


