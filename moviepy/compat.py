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

try:
    from os import fspath             # Python 3.6+
except ImportError:
    try:
        from pathlib import Path      # Python 3.4-3.5
    except ImportError:
        from pathlib2 import Path     # Python 3.3-
        from imageio.core import request
        
        request.Path = Path

    def fspath(path):
        if isinstance(path, (string_types, Path)):
            return str(path)
        raise TypeError("expected string or Path object, "
                        "not %s" % path.__class__.__name__)
