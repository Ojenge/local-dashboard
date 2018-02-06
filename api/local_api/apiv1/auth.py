# -*- coding: utf-8 -*-

from flask import current_app as app
from flask import request

from local_api.apiv1.utils import get_request_log
from local_api.apiv1.errors import APIError

from local_api.apiv1.models import check_header

AUTH_HEADER = 'X-Auth-Token-Key'


def unauthorized():
    app.logger.error("Unauthorized Access|%s",
                     get_request_log(request))
    raise APIError(message="Unauthorized",
                   errors=["Unauthorized access."],
                   status_code=401)



def load_user(r):
    """Loads authenticated used from API key.
    """
    _user = None
    key = r.headers.get(AUTH_HEADER)
    user = check_header(key)
    if user is not None:
        return user
    return _user