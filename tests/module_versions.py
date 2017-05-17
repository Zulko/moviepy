import os
import sys
import importlib

_required_modules=['moviepy', 'decorator', 'imageio', 'numpy', 'tqdm']

_optional_modules=['Pillow']

_one_of_many=[]

print("Platform: %s" % sys.platform)
print("Python Version: %s.%s" % (sys.version_info.major, sys.version_info.minor))
print("")

for _lib in _required_modules + _optional_modules:
    try:
       _mod=importlib.import_module(_lib)
       print("%s : %s" % (_lib, _mod.__version__))
    except ImportError:
       if _lib in _required_modules:
          print("%s is not installed (a REQUIRED module)" % _lib)
       else:
          print("%s is not installed (an optional module)" % _lib)
