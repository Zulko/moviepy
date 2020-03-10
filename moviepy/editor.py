"""
This file is meant to make it easy to load the main features of
MoviePy by simply typing:

>>> from moviepy.editor import *

In particular it will load many effects from the video.fx and audio.fx
folders and turn them into VideoClip methods, so that instead of
>>> clip.fx( vfx.resize, 2 ) # or equivalently vfx.resize(clip, 2)
we can write
>>> clip.resize(2)

It also starts a PyGame session (if PyGame is installed) and enables
clip.preview().
"""

# Note that these imports could have been performed in the __init__.py
# file, but this would make the loading of moviepy slower.

import os
import sys

# Downloads ffmpeg if it isn't already installed
import imageio
# Checks to see if the user has set a place for their own version of ffmpeg

if os.getenv('FFMPEG_BINARY') is None:
    if sys.version_info < (3, 4):
        #uses an old version of imageio with ffmpeg.download.
        imageio.plugins.ffmpeg.download()

# Hide the welcome message from pygame: https://github.com/pygame/pygame/issues/542
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "1"

# Clips
from .video.io.VideoFileClip import VideoFileClip
from .video.io.ImageSequenceClip import ImageSequenceClip
from .video.io.downloader import download_webfile
from .video.VideoClip import VideoClip, ImageClip, ColorClip, TextClip
from .video.compositing.CompositeVideoClip import CompositeVideoClip, clips_array
from .video.compositing.concatenate import concatenate_videoclips, concatenate # concatenate=deprecated

from .audio.AudioClip import AudioClip, CompositeAudioClip, concatenate_audioclips
from .audio.io.AudioFileClip import AudioFileClip

# FX

import moviepy.video.fx.all as vfx
import moviepy.audio.fx.all as afx
import moviepy.video.compositing.transitions as transfx

# Tools

import moviepy.video.tools as videotools
import moviepy.video.io.ffmpeg_tools as ffmpeg_tools
from .video.io.html_tools import ipython_display
from .tools import cvsecs

try:
    from .video.io.sliders import sliders
except ImportError:
    pass

# The next loop transforms many effects into VideoClip methods so that
# they can be walled with myclip.resize(width=500) instead of 
# myclip.fx( vfx.resize, width= 500)
for method in [
          "afx.audio_fadein",
          "afx.audio_fadeout",
          "afx.audio_normalize",
          "afx.volumex",
          "transfx.crossfadein",
          "transfx.crossfadeout",
          "vfx.crop",
          "vfx.fadein",
          "vfx.fadeout",
          "vfx.invert_colors",
          "vfx.loop",
          "vfx.margin",
          "vfx.mask_and",
          "vfx.mask_or",
          "vfx.resize",
          "vfx.rotate",
          "vfx.speedx"
          ]:

    exec("VideoClip.%s = %s" % (method.split('.')[1], method))


for method in ["afx.audio_fadein",
               "afx.audio_fadeout",
               "afx.audio_loop",
               "afx.audio_normalize",
               "afx.volumex"
              ]:
              
    exec("AudioClip.%s = %s" % (method.split('.')[1], method))


# adds easy ipython integration
VideoClip.ipython_display = ipython_display
AudioClip.ipython_display = ipython_display
#-----------------------------------------------------------------
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
