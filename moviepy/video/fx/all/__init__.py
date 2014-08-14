"""
Loads all the fx !
Usage:
import moviepy.video.fx.all as vfx
clip = vfx.resize(some_clip, width=400)
clip = vfx.mirror_x(some_clip)
"""

import os


_directory = os.path.dirname(
	            os.path.dirname(
	            	os.path.realpath(__file__)))

_files = os.listdir(_directory)
_fx_list = [_f for _f in _files if ( _f.endswith('.py') and
	                            not _f.startswith('_'))]

__all__ = [_c[:-3] for _c in _fx_list]

for _name in __all__:
    exec("from ..%s import %s"%(_name,_name))