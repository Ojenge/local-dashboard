# -*- coding: utf-8 -*-

from local_api.apiv1.schema import Validator

SIMPLE = dict(a=10)

SUPERSET = ['A', 'B', 'C']
PATTERN_A = '^(A|B|C)$'
PATTERN_B = '^C\d{2,4}$'

COMPLEX = dict(
    a=10,
    b=20,
    c=15,
    d='A'
)

def test_simple():
    v = Validator(SIMPLE)
    v.ensure_exists('a')
    v.ensure_range('a', 0, 10)
    assert v.is_valid
    v.ensure_range('a', 0, 10, int)
    assert v.is_valid
    v.ensure_range('a', 1, 5)
    assert v.is_valid is False
    assert 'a' in v.errors 


def test_complex():
    v = Validator(COMPLEX)
    v.ensure_exists('a')
    v.ensure_exists('b')
    v.ensure_exists('c')
    v.ensure_exists('d')
    assert v.is_valid
    v.ensure_range('b', 15, 25)
    assert v.is_valid
    v.ensure_less_than('a', 'b')
    assert v.is_valid
    v.ensure_less_than('b', 'c')
    assert v.is_valid is False
    v.ensure_inclusion('d', SUPERSET)
    assert v.is_valid is False
    assert 'd' not in v.errors
    v.ensure_format('d', PATTERN_A)
    assert 'd' not in v.errors
    v.ensure_format('d', PATTERN_B)
    assert 'd' in v.errors
 

def test_complex_complex():
    v = Validator(COMPLEX)
    v.required_together('a', 'b')
    assert v.is_valid
    v.required_together('a', 'e')
    assert v.is_valid is False
    assert 'e' in v.errors

