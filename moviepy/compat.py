import os
import sys
PY3=sys.version_info.major >= 3

try:
    string_types = (str, unicode)     # Python 2
except NameError:
    string_types = (str)              # Python 3
   
try:
    from subprocess import DEVNULL    # Python 3
except ImportError:
    DEVNULL = open(os.devnull, 'wb')  # Python 2
