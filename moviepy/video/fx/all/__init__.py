"""
moviepy.video.fx.all is deprecated.

.. deprecated:: 2.0.0
    Use the fx method directly from the clip instance (e.g. ``clip.resize(...)``)
    or import the function from moviepy.video.fx instead.
"""
import warnings

from moviepy.video.fx import *  # noqa F401,F403


warnings.warn(f"\nMoviePy: {__doc__}", UserWarning)
