# -*- coding: utf-8 -*-

"""
Utilities for interacting with the filesystem.
"""

import os

from functools import wraps
from werkzeug.contrib.cache import SimpleCache, NullCache


LOG = __import__('logging').getLogger()

MINUTE = 60
CACHE = SimpleCache()
if os.getenv('FLASK_TESTING'):
    CACHE = NullCache()


def cached(timeout=0):
    """Caches Result of Function Call
    """
    def decorated(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            arg_key = '-'.join([str(a) for a in args])
            cache_key = '{}/{}/{}'.format(f.__module__, f.__name__, arg_key)
            LOG.debug("Looking up cache: %r", cache_key)
            cached_val = CACHE.get(cache_key)
            if cached_val:
                LOG.debug("Cache HIT: %s", cache_key)
                return cached_val
            else:
                LOG.debug("Cache MISS: %s", cache_key)
                res = f(*args, **kwargs)
                CACHE.set(cache_key, res, timeout=timeout)
                return res
        return wrapped
    return decorated
