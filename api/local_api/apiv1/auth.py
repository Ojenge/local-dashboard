# -*- coding: utf-8 -*-

import os
from binascii import hexlify

from flask import current_app as app


AUTH_KEY_ENV = 'AUTHORIZED_KEY'
AUTH_HEADER = 'X-Auth-Token-Key'


def generate_key():
    """Generates an authentication key once 
    """
    auth_key = None
    if AUTH_KEY_ENV in app.config:
        auth_key = app.config[AUTH_KEY_ENV]
    else:
        auth_key = hexlify(os.urandom(64))
        app.config[AUTH_KEY_ENV] = auth_key
        app.logger.error("Authorization key to use for testing: %s", auth_key)
    return auth_key


class User(object):
    """Flask Login authentication class
    """
    
    login = None

    def __init__(self, login=None):
        self.login = login

    def is_authenticated(self):
        return self.login is not None

    def is_active(self):
        return self.login is not None

    def is_anonymous(self):
        return self.login is None

    def get_id(self):
        return unicode(self.login)


def load_user(request):
    """Loads authenticated used from API key.
    """
    _user = None
    key = request.headers.get(AUTH_HEADER)
    if key == os.environ.get(AUTH_KEY_ENV, generate_key()):
        return User('username')
    return _user