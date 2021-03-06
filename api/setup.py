# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name='brck-local-api',
    version='0.1-dev',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Flask',
    ],
    setup_requires=[
        'pytest-runner',
    ],
    tests_require=[
        'pytest',
    ],
)