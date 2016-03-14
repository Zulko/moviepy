"""
Loads all the fx !
Usage:
import moviepy.video.fx.all as vfx
clip = vfx.resize(some_clip, width=400)
clip = vfx.mirror_x(some_clip)
"""

import pkgutil
import os

__all__ = [name for _, name, _ in pkgutil.iter_modules(
    [os.path.join(__path__[0], "..")]) if name != "all"]

for _name in __all__:
    exec("from ..%s import %s"%(_name,_name))