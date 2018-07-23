# -*- coding: utf-8 -*-

from __future__ import print_function

from os import urandom
from binascii import hexlify

from flask_script import Manager
from flask_migrate import MigrateCommand
from local_api import app
from local_api.apiv1.models import create_user, delete_user
from local_api.apiv1.utils import get_device_mode

manager = Manager(app)
manager.add_command('db', MigrateCommand)


@manager.command
def add_admin_user():
    print('\n---------------------------\n')
    device_mode = get_device_mode()
    if device_mode == "RETAIL":
        print("Adding admin user...")
        status = create_user('admin', 'admin')
        if status:
            print('[SUCCESS] Admin user has been created')
        else:
            print(
                '[ERROR] Admin user creation failed. This may already have been done.'
            )
    else:
        print("Adding admin user disabled in non-retail mode")


@manager.command
def del_user(login):
    print('\n---------------------------\n')
    print("[INFO] Deleting user with login: {}".format(login))
    status = delete_user(login)
    if status:
        print("[SUCCESS] User with login [{}] deleted.".format(login))
    else:
        print("[ERROR] User with login [{}] not deleted.".format(login))


@manager.command
def add_root_user():
    print('\n---------------------------\n')
    print("Adding root user...")
    fake_root_pass = hexlify(urandom(64))
    status = create_user('root', fake_root_pass)
    if status:
        print('[SUCCESS] Root user has been created')
    else:
        print(
            '[ERROR] Root user creation failed. This may already have been done.'
        )


@manager.command
def add_diagnostics_user():
    print('\n---------------------------\n')
    print("Adding diagnostics user...")
    fake_diagnostics_pass = hexlify(urandom(64))
    status = create_user('diagnostics', fake_diagnostics_pass)
    if status:
        print('[SUCCESS] Diagnostics user has been created')
    else:
        print(
            '[ERROR] Diagnostics user creation failed. This may already have been done.'
        )


if __name__ == '__main__':
    manager.run()
