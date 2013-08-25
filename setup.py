#!/usr/bin/env python

from distutils.core import setup
setup(name='moviepy',
      version='0.1',
      author='Zulko 2013',
    description='Module for script-based video editing',
    long_description=open('README.txt').read(),
    license='LICENSE.txt',
    keywords="movie editing film mixing script-based",
    packages=['moviepy'],
    requires = ['scipy','numpy','matplotlib','pygame',
                'cv2 >=2.4.6','decorator'])
