#!/usr/bin/env python

# This will try to import setuptools. If not here, it will reach for the embedded
# ez_setup (or the ez_setup package). If none, it fails with a message
import sys
from codecs import open

try:
    from setuptools import find_packages, setup
    from setuptools.command.test import test as TestCommand
except ImportError:
    try:
        import ez_setup
        ez_setup.use_setuptools()
    except ImportError:
        raise ImportError('MoviePy could not be installed, probably because'
            ' neither setuptools nor ez_setup are installed on this computer.'
            '\nInstall ez_setup ([sudo] pip install ez_setup) and try again.')


class PyTest(TestCommand):
    """Handle test execution from setup."""

    user_options = [('pytest-args=', 'a', "Arguments to pass into pytest")]

    def initialize_options(self):
        """Initialize the PyTest options."""
        TestCommand.initialize_options(self)
        self.pytest_args = ""

    def finalize_options(self):
        """Finalize the PyTest options."""
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        """Run the PyTest testing suite."""
        try:
            import pytest
        except ImportError:
            raise ImportError('Running tests requires additional dependencies.'
                '\nPlease run (pip install moviepy[test])')

        errno = pytest.main(self.pytest_args.split(" "))
        sys.exit(errno)


cmdclass = {'test': PyTest} # Define custom commands.

if 'build_docs' in sys.argv:
    try:
        from sphinx.setup_command import BuildDoc
    except ImportError:
        raise ImportError('Running the documenation builds has additional'
            ' dependencies. Please run (pip install moviepy[docs])')

    cmdclass['build_docs'] = BuildDoc

__version__ = None # Explicitly set version to quieten static code checkers.
exec(open('moviepy/version.py').read()) # loads __version__

# Define the requirements for specific execution needs.
requires = [
    'decorator>=4.0.2,<5.0',
    "imageio>=2.5,<3.0; python_version>='3.4'",
    "imageio>=2.0,<2.5; python_version<'3.4'",
    "imageio_ffmpeg>=0.2.0; python_version>='3.4'",
    'tqdm>=4.11.2,<5.0',
    "numpy>=1.17.3; python_version!='2.7'",
    "numpy; python_version>='2.7'",
    'requests>=2.8.1,<3.0',
    'proglog<=1.0.0'
    ]

optional_reqs = [
        "opencv-python>=3.0,<4.0; python_version!='2.7'",
        "scikit-image>=0.13.0,<1.0; python_version>='3.4'",
        "scikit-learn; python_version>='3.4'",
        "scipy>=0.19.0,<1.5; python_version!='3.3'",
        "matplotlib>=2.0.0,<3.0; python_version>='3.4'",
        "youtube_dl"
        ]

doc_reqs = [
        "pygame>=1.9.3,<2.0; python_version<'3.8'",
        'numpydoc>=0.6.0,<1.0',
        'sphinx_rtd_theme>=0.1.10b0,<1.0', 
        'Sphinx>=1.5.2,<2.0',
    ]

test_reqs = [
        'coverage<5.0',
        'coveralls>=1.1,<2.0',
        'pytest-cov>=2.5.1,<3.0',
        'pytest>=3.0.0,<4.0',
        'requests>=2.8.1,<3.0'
    ]

extra_reqs = {
    "optional": optional_reqs,
    "doc": doc_reqs,
    "test": test_reqs
    }

# Load the README.
with open('README.rst', 'r', 'utf-8') as f:
    readme = f.read()

setup(
    name='moviepy',
    version=__version__,
    author='Zulko 2017',
    description='Video editing with Python',
    long_description=readme,
    url='https://zulko.github.io/moviepy/',
    license='MIT License',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Multimedia',
        'Topic :: Multimedia :: Sound/Audio',
        'Topic :: Multimedia :: Sound/Audio :: Analysis',
        'Topic :: Multimedia :: Video',
        'Topic :: Multimedia :: Video :: Capture',
        'Topic :: Multimedia :: Video :: Conversion',
    ],
    keywords='video editing audio compositing ffmpeg',
    packages=find_packages(exclude=['docs', 'tests']),
    cmdclass=cmdclass,
    command_options={
        'build_docs': {
            'build_dir': ('setup.py', './docs/build'),
            'config_dir': ('setup.py', './docs'),
            'version': ('setup.py', __version__.rsplit('.', 2)[0]),
            'release': ('setup.py', __version__)}},
    tests_require=test_reqs,
    install_requires=requires,
    extras_require=extra_reqs,
)
