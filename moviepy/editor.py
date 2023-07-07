"""
Module meant to make it easy to load the features of MoviePy that you will use
for live editing by simply typing:

>>> from moviepy.editor import *

- Enables ``clip.ipython_display()`` if in an IPython Notebook
- Allows the use of ``sliders`` if Matplotlib is installed
"""

import os

import moviepy  # So that we can access moviepy.__all__ later
from moviepy import *
from moviepy.video.io.html_tools import ipython_display



try:
    from moviepy.video.io.sliders import sliders
except ImportError:

    def sliders(*args, **kwargs):
        """NOT AVAILABLE: sliders requires matplotlib installed."""
        raise ImportError("sliders requires matplotlib installed")


# adds easy ipython integration
VideoClip.ipython_display = ipython_display
AudioClip.ipython_display = ipython_display


# Add methods preview and show (only if pygame installed)
try:
    from moviepy.video.io.preview import show, preview
except ImportError:

    def preview(self, *args, **kwargs):
        """NOT AVAILABLE: clip.preview requires Pygame installed."""
        raise ImportError("clip.preview requires Pygame installed")

    def show(self, *args, **kwargs):
        """NOT AVAILABLE: clip.show requires Pygame installed."""
        raise ImportError("clip.show requires Pygame installed")


VideoClip.preview = preview
VideoClip.show = show

try:
    from moviepy.audio.io.ffmpeg_audiopreviewer import ffmpeg_audiopreview
except ImportError:

    def preview(self, *args, **kwargs):
        """NOT AVAILABLE: clip.preview requires Pygame installed."""
        raise ImportError("clip.preview requires Pygame installed")


AudioClip.preview = ffmpeg_audiopreview

__all__ = moviepy.__all__ + ["ipython_display", "sliders"]

del show, preview, ffmpeg_audiopreview
