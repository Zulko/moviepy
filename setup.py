#!/usr/bin/env python

from setuptools import setup

setup(name='moviepy',
      version='0.1',
      author='Zulko 2013',
    description='Module for script-based video editing',
    long_description=open('README.rst').read(),
    license='LICENSE.txt',
    keywords="movie editing film mixing script-based",
    packages=['moviepy'],
    install_requires = ['scipy','numpy','matplotlib','pygame',
                'scikit-image','decorator', 'cython'])
