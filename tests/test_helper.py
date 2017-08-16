# -*- coding: utf-8 -*-
"""Define general test helper attributes and utilities."""
import os
import sys
import tempfile

TRAVIS = os.getenv("TRAVIS_PYTHON_VERSION") is not None
PYTHON_VERSION = "%s.%s" % (sys.version_info.major, sys.version_info.minor)
TMP_DIR = tempfile.gettempdir()   # because tempfile.tempdir is sometimes None

# Arbitrary font used in caption testing.
if sys.platform in ("win32", "cygwin"):
    FONT = "Arial"
    # Even if Windows users install the Liberation fonts, it is called LiberationMono on Windows, so
    # it doesn't help.
else:
    FONT = "Liberation-Mono" # This is available in the fonts-liberation package on Linux.

