"""
moviepy.video.fx.all is deprecated. 

Use the right fx method directly from the clip instance
or import the function from moviepy.video.fx instead. 
"""
import warnings

from .. import *

warnings.warn(f"MoviePy: {__doc__}", UserWarning)