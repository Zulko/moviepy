"""
Loads all the fx !
Usage:
import moviepy.video.fx.all as vfx
clip = vfx.resize(some_clip, width=400)
clip = vfx.mirror_x(some_clip)
"""

import os


directory = os.path.dirname(
	            os.path.dirname(
	            	os.path.realpath(__file__)))

files = os.listdir(directory)
fx_list = [f for f in files if ( f.endswith('.py') and not f.startswith('_'))]
__all__ = [c[:-3] for c in fx_list]

for name in __all__:
    exec("from ..%s import %s"%(name,name))