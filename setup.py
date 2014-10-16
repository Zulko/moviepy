#!/usr/bin/env python

import ez_setup
ez_setup.use_setuptools()

exec(open('moviepy/version.py').read()) # loads __version__

from setuptools import setup, find_packages

setup(name='moviepy',
    version=__version__,
    author='Zulko 2014',
    description='Video editing with Python',
    long_description=open('README.rst').read(),
    license='see LICENSE.txt',
    keywords="video editing audio compositing numpy ffmpeg ",
    packages= find_packages(exclude='docs'),
    install_requires= ['numpy', 'decorator', 'tqdm'])
