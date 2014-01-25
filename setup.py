#!/usr/bin/env python

import ez_setup
ez_setup.use_setuptools()

from setuptools import setup, find_packages

setup(name='moviepy',
      version='0.2.1.6.9',
      author='Zulko 2013',
    description='Module for script-based video editing',
    long_description=open('README.rst').read(),
    license='LICENSE.txt',
    keywords="movie editing film mixing script-based",
    packages= find_packages(exclude='docs'),
    requires=['numpy', 'decorator'])
