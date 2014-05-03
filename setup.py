#!/usr/bin/env python

import ez_setup
ez_setup.use_setuptools()

exec(open('moviepy/version.py').read()) # loads __version__

from setuptools import setup, find_packages

setup(name='moviepy',
    version=__version__,
    author='Zulko 2014',
    description='Module for script-based video editing',
    long_description=open('README.rst').read(),
    license='see LICENSE.txt',
    keywords="movie editing film mixing script-based",
    packages= find_packages(exclude='docs'),
    install_requires= ['numpy', 'decorator', 'tqdm'])
