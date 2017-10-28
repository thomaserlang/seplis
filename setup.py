#!/usr/bin/env python
import os
from setuptools import setup, find_packages

with open('requirements.txt') as f:
    install_requires = f.read().splitlines()

setup(
    name='seplis',
    version='0.1.8',
    author='Thomas Erlang',
    author_email='thomas@erlang.dk',
    url='https://github.com/thomaserlang/seplis',
    description='',
    long_description=__doc__,
    package_dir={'': 'src'},
    packages=find_packages('src'),
    zip_safe=False,
    install_requires=install_requires,
    license=None,
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'seplis = seplis.runner:main',
        ],
    },
    classifiers=[],
)
