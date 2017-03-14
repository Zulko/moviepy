import os
import sys

TRAVIS=os.getenv("TRAVIS_PYTHON_VERSION") is not None
PYTHON_VERSION = "%s.%s" % (sys.version_info.major, sys.version_info.minor)
TMP_DIR="/tmp"

