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


def cached(timeout=0, ignore=None):
    """Caches Result of function call.

    The cache key is generated from the function name any arguments.

    Args:
        timeout (int): Time in seconds to store the response in cache
        ignore (list(int), optional): List of values that would not be cached.

    Returns:
        function: Wrapped function

    """
    def decorated(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            arg_key = '-'.join([str(a) for a in args])
            cache_key = '{}/{}/{}'.format(f.__module__, f.__name__, arg_key)
            cached_val = None
            if kwargs.get('no_cache') != True:
                LOG.debug("Looking up cache: %r", cache_key)
                cached_val = CACHE.get(cache_key)
            if cached_val:
                LOG.debug("Cache HIT: %s", cache_key)
                return cached_val
            else:
                LOG.debug("Cache MISS: %s", cache_key)
                res = None
                try:
                    res = f(*args, **kwargs)
                except Exception as e:
                    LOG.error("Error calculating cached value: Raising: %e", e)
                    raise(e)
                _ignored = ignore or []
                if res and res not in _ignored:
                    CACHE.set(cache_key, res, timeout=timeout)
                return res
        return wrapped
    return decorated
