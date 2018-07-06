# -*- coding: utf-8 -*-

"""FTP Configuration
"""

import subprocess
import spwd
import pwd

from brck.utils import run_command

from .schema import Validator

FTP_DIRECTORY = '/storage/data/ftp'


def user_exists(login):
    user_with_home = filter(lambda p: p.pw_dir == FTP_DIRECTORY,
                            pwd.getpwall())
    if user_with_home:
        return user_with_home[0].pw_name
    login_name = None
    try:
        spwd.getspnam(login)
        login_name = login
    except KeyError:
        pass
    return login_name


def set_user_password(login, password):
    """Sets the user root password

    :param login: the password to assign to the login
    :param password: the password to assign to the login
    :rtype boolean
    """
    process = subprocess.Popen(['passwd', login],
                               stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
    process.stdin.write('{}\n'.format(password))
    process.stdin.write(password)
    process.stdin.flush()

    _, err = process.communicate()

    if err is None or len(err) == 0:
        return True
    return False


def create_user(login, password):
    return run_command(['adduser', '-D', '-H', '-h', FTP_DIRECTORY, login])


def configure_ftp(config):
    """Creates FTP user with home directory as FTP directory
    """
    v = Validator(config)
    v.ensure_exists('login', 'password')
    if v.is_valid:
        _login = config['login']
        _password = config['password']
        existing_user = user_exists(_login)
        if existing_user is None:
            if not create_user(_login, _password):
                v.add_error('login', 'Failed to set up user')
        else:
            if _login != existing_user:
                v.add_error('login', 'FTP user has already been set up')
        if v.is_valid:
            if not set_user_password(_login, _password):
                v.add_error('password', 'Failed to set user password')
    if v.is_valid:
        return (200, 'OK')
    else:
        return (422, v.errors)
