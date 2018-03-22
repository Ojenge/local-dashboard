# -*- coding: utf-8 -*-

import sys
import os

import local_api
from local_api.apiv1 import models

# inject syspath
file_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(file_dir, '../'))


def test_delete_user():
    test_login = test_password = 'delete_me'
    local_api.db.create_all()
    assert models.delete_user(test_login) == False
    models.create_user(test_login, test_password)
    assert models.check_password(test_login, test_password) == True
    assert models.delete_user(test_login) == True
    assert models.check_password(test_login, test_password) == False