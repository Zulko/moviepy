"""
Contains transformation functions (clip->clip)
One file for one fx. The file's name is the fx's name
"""

import os

directory = os.path.dirname(os.path.realpath(__file__))
files = os.listdir(directory)
fx_list = [f for f in files if ( f.endswith('.py') and not f.startswith('_'))]
__all__ = [c[:-3] for c in fx_list]

for name in __all__:
    exec("from .%s import %s"%(name,name))
