# -*- coding: utf-8 -*-

from __future__ import print_function

from flask_script import Manager
from local_api import app
from local_api.apiv1.models import create_user

manager = Manager(app)

@manager.command
def add_admin_user():
    print('\n---------------------------\n')
    print("Adding admin user...")
    status = create_user('admin', 'admin')
    if status:
        print('[SUCCESS] Admin user has been created')
    else:
        print('[ERROR] Admin user creation failed. This may already have been done.')

if __name__ == '__main__':
    manager.run()
    
