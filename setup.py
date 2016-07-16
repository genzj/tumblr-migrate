#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


with open('README.rst') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='tumblr-migrate',
    version='0.1.0',
    description='Migrate your tumblr followings and likes to another account',
    long_description=readme,
    author='Genzj',
    author_email='zj0512@gmail.com',
    url='https://github.com/genzj/tumblr-migrate',
    license=license,
    packages=find_packages(exclude=('tests', 'docs'))
)

