# -*- coding: utf-8 -*-

class APIError(Exception):
    """Common API Error
    """

    def __init__(self, message='Error', errors=[], status_code=400):
        Exception.__init__(self)
        self.message = message
        self.status_code = status_code
        self.errors = errors

    def to_dict(self):
        r = {}
        r['message'] = self.message
        r['errors'] = self.errors
        return r
