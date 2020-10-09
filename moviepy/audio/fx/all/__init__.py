"""
moviepy.audio.fx.all is deprecated. 

Use the fx method directly from the clip instance (e.g. ``clip.audio_loop(...)``)
or import the function from moviepy.audio.fx instead. 
"""
import warnings

from .. import *

warnings.warn(f"\nMoviePy: {__doc__}", UserWarning)
