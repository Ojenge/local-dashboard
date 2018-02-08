# -*- coding: utf-8 -*-

import re

class Validator(object):
    """Performs validation of a dictionary of values.

    Populates an errors context.
    """

    def __init__(self, data):
        self.data = data
        self.errors = {}

    @property
    def is_valid(self):
        return len(self.errors) == 0

    def add_error(self, key, message):
        self.errors[key] = message

    def add_errors(self, errors):
        self.errors.update(errors)

    def ensure_exists(self, key, message=None):
        if key not in self.data and key not in self.errors:
            self.errors[key] = message or '{} required'.format(key)

    def ensure_excluded(self, *keys):
        for key in keys:
            if key in self.data:
                self.errors[key] = '{} not required'.format(key)
    
    def ensure_format(self, key, pattern):
        if key not in self.errors:
            v = self.data.get(key, '')
            if not re.match(pattern, v):
                self.errors[key] = 'Invalid format'

    def ensure_exact(self, key, expected):
        if key not in self.errors:
            v = self.data.get(key, '')
            if key != expected:
                self.errors[key] = 'must be: {}'.format(expected)
   
    def required_together(self, *keys):
        missing = []
        for k in keys:
            if (not k in self.errors) and (not self.data.get(k)):
                missing.append([k, 'required'])
        if len(missing) < len(keys):
            self.errors.update(missing)

    def ensure_not_equal(self, key_a, key_b):
        v0 = self.data.get(key_a, '')
        v1 = self.data.get(key_b, '')
        if v0 == v1:
            self.errors[key_a] = 'must not be equal to: %s' % key_b
            self.errors[key_b] = 'must not be equal to: %s' % key_a
 
    def ensure_range(self, key, min, max, type=None):
        if not key in self.errors:
            v = self.data.get(key)
            if type and not isinstance(v, type):
                self.errors['key'] = 'invalid type'
            else:
                if not(v >= min and v <= max):
                    self.errors[key] = 'must be between {} and {}'.format(min, max)

    def ensure_less_than(self, key_a, key_b):
        if not (key_a in self.errors or key_b in self.errors):
            v_a = self.data.get(key_a, 0)
            v_b = self.data.get(key_b, 0)
            if v_a >= v_b:
                self.errors[key_a] = 'must be less than {}'.format(key_b)
                self.errors[key_b] = 'must be greater than {}'.format(key_b)

    def ensure_inclusion(self, key, superset, required=True):
        if key not in self.errors:
            v = self.data.get(key)
            if v not in superset and required:
                options = ','.join(superset)
                self.errors[key] = 'must be one of {}'.format(options)