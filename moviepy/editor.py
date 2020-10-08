"""
This file is meant to make it easy to load the main features of
MoviePy by simply typing:

>>> from moviepy.editor import *

In particular it will load many effects from the video.fx and audio.fx
folders and turn them into VideoClip methods, so that instead of
>>> clip.fx( vfx.resize, 2 ) or equivalently vfx.resize(clip, 2)
we can write
>>> clip.resize(2)

It also starts a PyGame session (if PyGame is installed) and enables
clip.preview().
"""

__all__ = [
    "afx",
    "AudioClip",
    "AudioFileClip",
    "BitmapClip",
    "clips_array",
    "ColorClip",
    "CompositeAudioClip",
    "CompositeVideoClip",
    "concatenate_audioclips",
    "concatenate_videoclips",
    "convert_to_seconds",
    "download_webfile",
    "ffmpeg_tools",
    "ImageClip",
    "ImageSequenceClip",
    "ipython_display",
    "TextClip",
    "transfx",
    "vfx",
    "VideoClip",
    "VideoFileClip",
    "videotools",
]

# Note that these imports could have been performed in the __init__.py
# file, but this would make the loading of moviepy slower.

import os
import inspect


# Hide the welcome message from pygame: https://github.com/pygame/pygame/issues/542
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

# Clips
from .video.io.VideoFileClip import VideoFileClip
from .video.io.ImageSequenceClip import ImageSequenceClip
from .video.io.downloader import download_webfile
from .video.VideoClip import VideoClip, ImageClip, ColorClip, TextClip, BitmapClip
from .video.compositing.CompositeVideoClip import CompositeVideoClip, clips_array
from .video.compositing.concatenate import concatenate_videoclips

from .audio.AudioClip import AudioClip, CompositeAudioClip, concatenate_audioclips
from .audio.io.AudioFileClip import AudioFileClip

# FX

import moviepy.video.fx as vfx
import moviepy.audio.fx as afx
import moviepy.video.compositing.transitions as transfx

# Tools

import moviepy.video.tools as videotools
import moviepy.video.io.ffmpeg_tools as ffmpeg_tools
from .video.io.html_tools import ipython_display
from .tools import convert_to_seconds

try:
    from .video.io.sliders import sliders

    __all__.append("sliders")
except ImportError:
    pass

# Transforms the effects into Clip methods so that
# they can be called with clip.resize(width=500) instead of
# clip.fx(vfx.resize, width=500)
audio_fxs = inspect.getmembers(afx, inspect.isfunction)
video_fxs = (
    inspect.getmembers(vfx, inspect.isfunction)
    + inspect.getmembers(transfx, inspect.isfunction)
    + audio_fxs
)

for name, function in video_fxs:
    setattr(VideoClip, name, function)

for name, function in audio_fxs:
    setattr(AudioClip, name, function)


# adds easy ipython integration
VideoClip.ipython_display = ipython_display
AudioClip.ipython_display = ipython_display
# -----------------------------------------------------------------
# Previews: try to import pygame, else make methods which raise
# exceptions saying to install PyGame


# Add methods preview and show (only if pygame installed)
try:
    from moviepy.video.io.preview import show, preview
except ImportError:

    def preview(self, *args, **kwargs):
        """NOT AVAILABLE : clip.preview requires Pygame installed."""
        raise ImportError("clip.preview requires Pygame installed")

    def show(self, *args, **kwargs):
        """NOT AVAILABLE : clip.show requires Pygame installed."""
        raise ImportError("clip.show requires Pygame installed")


VideoClip.preview = preview
VideoClip.show = show

try:
    from moviepy.audio.io.preview import preview
except ImportError:

    def preview(self, *args, **kwargs):
        """ NOT AVAILABLE : clip.preview requires Pygame installed."""
        raise ImportError("clip.preview requires Pygame installed")


AudioClip.preview = preview
