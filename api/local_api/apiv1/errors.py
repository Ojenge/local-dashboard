# -*- coding: utf-8 -*-


class APIError(Exception):
    """Common API Error
    """

    def __init__(self, message='Error', errors=None, status_code=400):
        Exception.__init__(self)
        self.message = message
        self.status_code = status_code
        self.errors = errors or {}

    def to_dict(self):
        """Build response dictionary.
        
        This will be jsonified.
        """
        resp = {}
        resp['message'] = self.message
        resp['errors'] = self.errors
        return resp
