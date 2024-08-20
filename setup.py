#!/usr/bin/env python

# This will try to import setuptools. If not here, it will reach for the embedded
# ez_setup (or the ez_setup package). If none, it fails with a message
from codecs import open

try:
    from setuptools import find_packages, setup
    from setuptools.command.test import test
except ImportError:
    try:
        import ez_setup
        ez_setup.use_setuptools()
    except ImportError:
        raise ImportError('MoviePy could not be installed, probably because'
            ' neither setuptools nor ez_setup are installed on this computer.'
            '\nInstall ez_setup ([sudo] pip install ez_setup) and try again.')


__version__ = None # Explicitly set version to quieten static code checkers.
exec(open('minimal_moviepy/version.py').read()) # loads __version__

# Define the requirements for specific execution needs.
requires = [
    'decorator>=4.0.2,<5.0',
    "imageio>=2.5,<3.0; python_version>='3.4'",
    "imageio>=2.0,<2.5; python_version<'3.4'",
    "imageio_ffmpeg>=0.2.0; python_version>='3.4'",
    "numpy>=1.17.3,<=1.24.3; python_version!='2.7'",
    ]

# Load the README.
with open('README.rst', 'r', 'utf-8') as f:
    readme = f.read()

setup(
    name='minimal_moviepy',
    version=__version__,
    author='Zulko 2017',
    description='Video editing with Python',
    url='https://zulko.github.io/moviepy/',
    license='MIT License',
    packages=find_packages(),
    install_requires=requires,
)
