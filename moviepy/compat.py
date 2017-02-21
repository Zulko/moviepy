import os
import sys
PY3=sys.version_info.major >= 3

if PY3:
   from subprocess import DEVNULL  # py3k
else:
   DEVNULL = open(os.devnull, 'wb')
